from .json_data import JsonData
from .environment import Environment

# import in code
#from .service_proxy import ServiceProxy

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


class ConnectionBase(JsonData):
    """
    Represents connction to a remote machine or local, provides
    hide difference between local and remote
    """
    def __init__(self, config={}):

        self.address=""
        """ IP or hostname"""
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

        self._local_service = None
        """local service"""

    def set_local_service(self, local_service):
        self._local_service = local_service


class ConnectionLocal(ConnectionBase):
    def __init__(self, config={}):
        super().__init__(config)

    def connect(self):
        pass

    def forward_local_port(self, remote_port):
        """
        Get free local port and open SSH tunel for forwarding connection
        to the local port to the given 'remote port'.
        :param remote_port:
        :return: local_port
        """
        return remote_port


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

        return self._local_service

    def close_connections(self):
        """
        Close al connections in peaceful meaner.
        :param self:
        :return:
        """
        return

    def _copy(self, paths, from_prefix, to_prefix):
        if from_prefix == to_prefix:
            return
        for path in paths:
            to_file = os.path.join(to_prefix, path)
            os.makedirs(os.path.dirname(to_file), exist_ok=True)
            shutil.copyfile(os.path.join(from_prefix, path), to_file)


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

        self._delegator_proxy = None
        """delegator proxy"""

        self._delegator_std_in_out_err = None
        """delegator stdin, stdout, stderr"""

        self._sftp = None
        """SFTP session"""

        self._delegator_dir = ""
        """directory where delegator is executed"""

    def connect(self):
        """
        :raises SSHAuthenticationError:
        :raises SSHError:
        """
        # open ssh connection
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

        try:
            self._ssh.connect(self.address, self.port, username=self.uid, password=self.password, timeout=self._timeout)
        except paramiko.AuthenticationException:
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
        return remote_port

    def close_forwarded_remote_port(self, remote_port):
        """
        Close forwarded remote port.
        :param remote_port:
        :return:
        """
        self._ssh.get_transport().cancel_port_forward('', remote_port)

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
        self._sftp.chdir(cwd)

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
        for path in paths:
            loc = os.path.join(local_prefix, path)
            rem = os.path.join(remote_prefix, path)
            os.makedirs(os.path.dirname(loc), exist_ok=True)
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
                from .service_proxy import ServiceProxy
                self._delegator_proxy = ServiceProxy({}, self._local_service._repeater, self)
                self._delegator_proxy._child_id = child_id
                self._delegator_proxy.on_answer_connect()
                self._local_service._delegator_services[child_id] = self._delegator_proxy
                break

        return self._delegator_proxy

    def close_connections(self):
        """
        Close al connections in peaceful meaner.
        :param self:
        :return:
        """
        # close all forwarded local ports
        for port in list(self._forwarded_local_ports.keys()):
            self.close_forwarded_local_port(port)

        if self._sftp is not None:
            self._sftp.close()
            self._sftp = None

        self._ssh.close()




