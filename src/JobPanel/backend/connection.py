from .json_data import JsonData
from .environment import Environment

# import in code
#from .service_proxy import DelegatorProxy
#from .service_base import ServiceStatus

import paramiko

import shutil
import os
import os.path
import threading
import logging
import errno
import select
import socket
import socketserver
import time
import enum
import stat


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class SSHError(Error):
    """Raised when error in SSH session."""
    pass


class SSHAuthenticationError(SSHError):
    """Raised when authentication fail."""
    pass


class SSHTimeoutError(SSHError):
    """Raised when timeout occurs."""
    pass


class ConnectionStatus(enum.IntEnum):
    not_connected = 1
    online = 2
    offline = 3
    error = 4


class ConnectionBase(JsonData):
    """
    Represents connction to a remote machine or local, provides
    hide difference between local and remote
    """
    def __init__(self, config={}):

        self.address=""
        """ IP or hostname of SSH server ( localhost for LocalConnection)"""
        self.port=22
        """port for ssh connection"""
        self.uid=""
        """ user id for ssh connection """
        self.password=""
        """ password for ssh connection """
        self.environment = Environment()
        """ Seems that only path to the installation is necesary, possibly path to python."""
        self.name=""
        """ Unique name used in GUI."""
        super().__init__(config)

        self._status = ConnectionStatus.not_connected
        """connection status"""

        self._id = 0
        """connection id"""

        self._local_service = None
        """local service"""

        self._delegator_proxy = None
        """delegator proxy"""

    def get_status(self):
        return self._status

    def connect(self):
        self._status = ConnectionStatus.online
        self._id += 1

    def close_connections(self):
        """
        Close al connections in peaceful meaner.
        :param self:
        :return:
        """
        self._status = ConnectionStatus.not_connected

    def set_local_service(self, local_service):
        self._local_service = local_service


class ConnectionLocal(ConnectionBase):
    def __init__(self, config={}):
        super().__init__(config)

    def forward_local_port(self, remote_port):
        """
        Get free local port and open SSH tunel for forwarding connection
        to the local port to the given 'remote port'.
        :param remote_port:
        :return: local_port
        """
        return remote_port

    def close_forwarded_local_port(self, local_port):
        """
        Close forwarded local port.
        :param local_port:
        :return:
        """
        pass

    def forward_remote_port(self, local_port):
        """
        Try to open SSH tunel for forwarding connection
        from a remote port to the given 'local_port'.
        Remote port is first choosen same as the local port, but if tunneling fail
        we repeat with higher port (fixed number of tries).
        :param local_port:
        :return: remote_port
        """
        return local_port

    def close_forwarded_remote_port(self, remote_port):
        """
        Close forwarded remote port.
        :param remote_port:
        :return:
        """
        pass

    def upload(self,  paths, local_prefix, remote_prefix  ):
        """
        Upload given relative 'paths' to remote, prefixing them by 'local_prefix' for source and
        by 'remote_prefix' for destination.
        If target exists, replace it.
        :return: None
        :raises FileNotFoundError:
        :raises PermissionError:

        Implementation: just copy
        """
        self._copy(paths, local_prefix, remote_prefix)


    def download(self, paths, local_prefix, remote_prefix):
        """
        Download given relative 'paths' to remote, prefixing them by 'local_prefix' for destination and
        by 'remote_prefix' for source.
        If target exists, replace it.
        :return: None
        :raises FileNotFoundError:
        :raises PermissionError:

        Implementation: just copy
        """
        self._copy(paths, remote_prefix, local_prefix )

    def get_delegator(self):
        """
        Start delegator and return its proxy.

        We assume that Service itself can behave as ServiceProxy but not vice versa.
        :return: service_proxy
        """
        assert self._local_service is not None

        self._delegator_proxy = self._local_service

        return self._delegator_proxy

    def _copy(self, paths, from_prefix, to_prefix):
        if from_prefix == to_prefix:
            return
        for path in paths:
            src = os.path.join(from_prefix, path)
            dst = os.path.join(to_prefix, path)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if os.path.isdir(src):
                self._copy_dir(src, dst)
            else:
                shutil.copyfile(src, dst)

    def _copy_dir(self, src, dst):
        names = os.listdir(src)
        os.makedirs(dst, exist_ok=True)
        for name in names:
            srcname = os.path.join(src, name)
            dstname = os.path.join(dst, name)
            if os.path.isdir(srcname):
                self._copy_dir(srcname, dstname)
            else:
                shutil.copyfile(srcname, dstname)


class ConnectionSSH(ConnectionBase):


    def __init__(self, config={}):
        """
        :param config:
        """
        super().__init__(config)

        self._timeout = 1000
        """timeout for ssh operations"""

        self._forwarded_local_ports = {}
        """dict of forwarded local ports, {'local_port': (thread, server)}"""

        self._forwarded_remote_ports = set()
        """set of forwarded remote ports"""

        self._delegator_std_in_out_err = None
        """delegator stdin, stdout, stderr"""

        self._ssh = None
        """ssh client"""

        self._sftp = None
        """SFTP session"""

        self._delegator_dir = ""
        """directory where delegator is executed"""

        # reconnect thread, lock and event
        self._reconnect_thread = None
        self._reconnect_lock = threading.Lock()
        self._reconnect_event = threading.Event()

        #self._authentication_fail = False

    def get_status(self):
        if self._status == ConnectionStatus.online:
            proxy_status = self._delegator_proxy.get_status()
            from .service_base import ServiceStatus
            if proxy_status == ServiceStatus.done:
                self.close_connections()
                self._status = ConnectionStatus.offline
                self._reconnect_thread = threading.Thread(target=self._reconnect, daemon=True)
                self._reconnect_event.clear()
                self._reconnect_thread.start()
        return self._status

    def connect(self):
        """
        :raises SSHAuthenticationError:
        :raises SSHError:
        """
        if self._status == ConnectionStatus.error:
            raise SSHError

        # open ssh connection
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

        try:
            self._ssh.connect(self.address, self.port, username=self.uid, password=self.password, timeout=self._timeout)
        except paramiko.AuthenticationException:
            self._status = ConnectionStatus.error
            raise SSHAuthenticationError
        except (paramiko.SSHException, socket.error):
            raise SSHError
        except Exception as e:
            logging.error('*** Failed to connect to %s:%d: %r' % (self.address, self.port, e))
            raise

        # open an SFTP session
        self._sftp = self._ssh.open_sftp()
        self._sftp.get_channel().settimeout(self._timeout)

        # prepare workspace
        workspace = self.environment.geomop_analysis_workspace
        try:
            self._sftp.chdir(workspace)
        except IOError as e:
            self._sftp.mkdir(workspace)
        self._delegator_dir = os.path.join(workspace, "Delegators")
        try:
            self._sftp.chdir(self._delegator_dir)
        except IOError as e:
            self._sftp.mkdir(self._delegator_dir)
        self._sftp.chdir()

        assert self.get_delegator() is not None

        self._id += 1
        self._status = ConnectionStatus.online

    def _reconnect(self):
        while True:
            with self._reconnect_lock:
                if self._status == ConnectionStatus.offline:
                    try:
                        self.connect()
                        break
                    except:
                        pass
                else:
                    break
            #time.sleep(2)
            self._reconnect_event.wait(timeout=2)

    def __del__(self):
        # close all tunels, delagators, etc. immediately
        self.close_connections()

    # def is_alive(self):
    #     """
    #     Check if SSH connection is still alive.
    #     :return:
    #     """
    #     transport = self._ssh.get_transport()
    #     if transport.is_active():
    #         try:
    #             transport.send_ignore()
    #             return True
    #         except EOFError:
    #             pass
    #     return False

    def forward_local_port(self, remote_port):
        """
        Get free local port and open SSH tunel for forwarding connection
        to the local port to the given 'remote port'.
        :param remote_port:
        :return: local_port
        """

        # if self._status != ConnectionStatus.online:
        #     raise SSHError

        class ForwardServer(socketserver.ThreadingTCPServer):
            daemon_threads = True
            allow_reuse_address = True

        class Handler(socketserver.BaseRequestHandler):
            ssh_transport = self._ssh.get_transport()

            def handle(self):
                """
                This function must do all the work required to service a request.
                It is called for every request.
                """
                try:
                    chan = self.ssh_transport.open_channel('direct-tcpip',
                                                           ("localhost", remote_port),
                                                           self.request.getpeername())
                except Exception as e:
                    logging.error('Incoming request to %s:%d failed: %s' % ("localhost",
                                                                            remote_port,
                                                                            repr(e)))
                    return
                if chan is None:
                    logging.error('Incoming request to %s:%d was rejected by the SSH server.' %
                                  ("localhost", remote_port))
                    return

                logging.info('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
                                                                         chan.getpeername(),
                                                                         ("localhost", remote_port)))
                while True:
                    r, w, x = select.select([self.request, chan], [], [])
                    if self.request in r:
                        data = self.request.recv(1024)
                        if len(data) == 0:
                            break
                        chan.send(data)
                    if chan in r:
                        data = chan.recv(1024)
                        if len(data) == 0:
                            break
                        self.request.send(data)

                peername = self.request.getpeername()
                chan.close()
                self.request.close()
                logging.info('Tunnel closed from %r' % (peername,))

        # port 0 means to select an arbitrary unused port
        server = ForwardServer(('', 0), Handler)
        local_port = server.server_address[1]

        # start server in thread
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()

        # add thread and server to dict
        self._forwarded_local_ports[local_port] = (t, server)

        return local_port

    def close_forwarded_local_port(self, local_port):
        """
        Close forwarded local port.
        :param local_port:
        :return:
        """
        if local_port in self._forwarded_local_ports:
            # shutdown server
            t, server = self._forwarded_local_ports[local_port]
            server.shutdown()
            server.server_close()

            # wait for server's thread ends
            t.join(1.0)
            if t.is_alive():
                logging.error("Server's thread stopping timeout")

            # remove from dict
            del self._forwarded_local_ports[local_port]

    def forward_remote_port(self, local_port):
        """
        Get free remote port and open SSH tunel for forwarding connection
        from a remote port to the given 'local_port'.
        :param local_port:
        :return: remote_port
        :raises SSHError:
        """

        # if self._status != ConnectionStatus.online:
        #     raise SSHError

        def handler(chan, origin, server):
            def inner_handler():
                sock = socket.socket()
                try:
                    sock.connect(("localhost", local_port))
                except Exception as e:
                    logging.error('Forwarding request to %s:%d failed: %r' % ("localhost", local_port, e))
                    return

                logging.info('Connected!  Tunnel open %r -> %r -> %r' % (chan.origin_addr,
                                                                         chan.getpeername(), ("localhost", local_port)))
                while True:
                    r, w, x = select.select([sock, chan], [], [])
                    if sock in r:
                        data = sock.recv(1024)
                        if len(data) == 0:
                            break
                        chan.send(data)
                    if chan in r:
                        data = chan.recv(1024)
                        if len(data) == 0:
                            break
                        sock.send(data)
                chan.close()
                sock.close()
                logging.info('Tunnel closed from %r' % (chan.origin_addr,))

            t = threading.Thread(target=inner_handler)
            t.daemon = True
            t.start()

        try:
            remote_port = self._ssh.get_transport().request_port_forward('', 0, handler)
        except paramiko.SSHException:
            raise SSHError

        self._forwarded_remote_ports.add(remote_port)

        return remote_port

    def close_forwarded_remote_port(self, remote_port):
        """
        Close forwarded remote port.
        :param remote_port:
        :return:
        """
        if self._status != ConnectionStatus.online:
            return

        if remote_port in self._forwarded_remote_ports:
            self._ssh.get_transport().cancel_port_forward('', remote_port)
            self._forwarded_remote_ports.remove(remote_port)

    def upload(self, paths, local_prefix, remote_prefix):
        """
        Upload given relative 'paths' to remote, prefixing them by 'local_prefix' for source and
        by 'remote_prefix' for destination.
        If target exists, replace it.
        :return: None
        :raises FileNotFoundError:
        :raises PermissionError:
        :raises SSHTimeoutError:

        Implementation: just copy
        """
        assert os.path.isabs(remote_prefix)

        if self._status != ConnectionStatus.online:
            raise SSHError

        cwd = self._sftp.getcwd()
        for path in paths:
            # make dirs
            dir = os.path.dirname(path)
            dir_list = []
            while len(dir) > 0:
                dir_list.insert(0, dir)
                dir = os.path.dirname(dir)
            for dir in dir_list:
                prefix_dir = os.path.join(remote_prefix, dir)
                try:
                    self._sftp.chdir(prefix_dir)
                except IOError:
                    self._sftp.mkdir(prefix_dir)

            loc = os.path.join(local_prefix, path)
            rem = os.path.join(remote_prefix, path)
            if os.path.isdir(loc):
                self._upload_dir(loc, rem)
            else:
                self._upload_file(loc, rem)
        self._sftp.chdir(cwd)

    def _upload_file(self, loc, rem):
        try:
            self._sftp.put(loc, rem)
        except FileNotFoundError as e:
            if e.filename is None:
                raise OSError(errno.ENOENT, "No such remote file", rem)
            else:
                raise
        except PermissionError as e:
            if e.filename is None:
                raise OSError(errno.EACCES, "Permission denied on remote file", rem)
            else:
                raise
        except socket.timeout:
            raise SSHTimeoutError
        except OSError:
            raise SSHError

    def _upload_dir(self, loc, rem):
        names = os.listdir(loc)
        try:
            self._sftp.chdir(rem)
        except IOError:
            self._sftp.mkdir(rem)
        for name in names:
            loc_name = os.path.join(loc, name)
            rem_name = os.path.join(rem, name)
            if os.path.isdir(loc_name):
                self._upload_dir(loc_name, rem_name)
            else:
                self._upload_file(loc_name, rem_name)

    def download(self, paths, local_prefix, remote_prefix):
        """
        Download given relative 'paths' to remote, prefixing them by 'local_prefix' for destination and
        by 'remote_prefix' for source.
        If target exists, replace it.
        :return: None
        :raises FileNotFoundError:
        :raises PermissionError:
        :raises SSHTimeoutError:

        Implementation: just copy
        """
        if self._status != ConnectionStatus.online:
            raise SSHError

        for path in paths:
            loc = os.path.join(local_prefix, path)
            rem = os.path.join(remote_prefix, path)
            os.makedirs(os.path.dirname(loc), exist_ok=True)
            if stat.S_ISDIR(self._sftp.stat(rem).st_mode):
                self._download_dir(loc, rem)
            else:
                self._download_file(loc, rem)

    def _download_file(self, loc, rem):
        try:
            self._sftp.get(rem, loc)
        except FileNotFoundError as e:
            if e.filename is None:
                raise OSError(errno.ENOENT, "No such remote file", rem)
            else:
                raise
        except PermissionError as e:
            if e.filename is None:
                raise OSError(errno.EACCES, "Permission denied on remote file", rem)
            else:
                raise
        except socket.timeout:
            raise SSHTimeoutError
        except OSError:
            raise SSHError

    def _download_dir(self, loc, rem):
        os.makedirs(loc, exist_ok=True)
        for fileattr in self._sftp.listdir_attr(rem):
            loc_name = os.path.join(loc, fileattr.filename)
            rem_name = os.path.join(rem, fileattr.filename)
            if stat.S_ISDIR(fileattr.st_mode):
                self._download_dir(loc_name, rem_name)
            else:
                self._download_file(loc_name, rem_name)

    def get_delegator(self):
        """
        Start delegator and return its proxy.
        MJ and Backand seeervices should be derived from Delegator service or have delegator instance
        so that we can process requests processed by remote delegator localy.

        Process of starting a delegator
        1. Open remote forwarding tunnel (get local port from local_service.repeater.starter_server_port]
        2. Get child ID from repeater ( local_service.repeater.add_child(...) )
        3. Start delegator on remote using SSH exec. Pass: child ID, starter address
           (Delegater connect to local repeater, ClientDispatcher gets listenning port of the delegator)
        4. wait a bit
        5. call delegator_proxy.connect_service( child_id)
        6. store the delegator proxy in connection return it if asked next time

        :param local_service: Instance of ServiceBase (or derived class)
        :raises SSHError:
        :raises SSHTimeoutError:

        """

        assert self._local_service is not None

        if self._delegator_proxy is not None:
            """
            TODO:
            """
            return self._delegator_proxy

        # 1.
        # moved to repeater.add_child

        # 2.
        child_id, remote_port = self._local_service._repeater.add_child(self)

        # 3.
        command = 'cd "' + self._delegator_dir + '";' \
                  + self.environment.python + " " \
                  + os.path.join(self.environment.geomop_root, "JobPanel/services/delegator_service.py") \
                  + " {} {} {}".format(child_id, "localhost", remote_port)
        try:
            self._delegator_std_in_out_err = self._ssh.exec_command(command, timeout=self._timeout, get_pty=True)
        except paramiko.SSHException:
            raise SSHError
        except socket.timeout:
            raise SSHTimeoutError

        #time.sleep(10)
        #print(self._delegator_std_in_out_err[1].readlines())

        connected = False
        for i in range(100):
            time.sleep(0.1)
            answers = self._local_service._repeater.get_answers(child_id)
            for answer in answers:
                if answer.id == 0:
                    connected = True
                    break
            if connected:
                from .service_proxy import DelegatorProxy
                self._delegator_proxy = DelegatorProxy({}, self._local_service._repeater, self)
                self._delegator_proxy._child_id = child_id
                self._delegator_proxy.on_answer_connect()
                #self._local_service._delegator_services[child_id] = self._delegator_proxy
                break

        return self._delegator_proxy

    def close_connections(self):
        """
        Close al connections in peaceful meaner.
        :param self:
        :return:
        """
        with self._reconnect_lock:
            if self._status != ConnectionStatus.error:
                self._status = ConnectionStatus.not_connected
        self._reconnect_event.set()
        if self._reconnect_thread is not None:
            self._reconnect_thread.join()

        # close delegator proxi
        if self._delegator_proxy is not None:
            self._delegator_proxy.close()
            self._delegator_proxy = None

        # close all forwarded local ports
        for port in list(self._forwarded_local_ports.keys()):
            self.close_forwarded_local_port(port)

        self._forwarded_remote_ports.clear()

        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        if self._ssh is not None:
            self._ssh.close()
            self._ssh = None




