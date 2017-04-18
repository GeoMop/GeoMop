from .json_data import JsonData
from ._service_proxy import ServiceProxy

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


class Environment(JsonData):
    """
    Represents GeoMop backend installation and system configuration.

    Keep information about all executables that are part of the installation,
    metainformation about executables and scripts.
    (Can run given executable)

    Process of initialization. Environment configuration should be part of
    connection as it is related to particular machine. Still allowing to
    copy one connection to other and reuse environment or ssh.
    1. User set root dir.
    2. Default list of executables and other parts of configuration is test
    on the remote (using delegator) and returned back. Possible problems can be resolved
    by user manualy and further tested in a Connection panel.
    """

    def __init__(self, config={}):
        """
        If config have 'version_id' we just check that it match
        the version installed at 'root'. Otherwise we start test_installation.
        :param config: InstallationData
        """
        self.root = []
        """
        Path to the root directory of the GeoMop backend installtion.
        The only attribute that must be provided by user.
        """
        self.version_id = ""
        """ Version ID of the installation. This is set by 'test_installation'
        and checked against true state of the installation in constructor."""
        self.executables = []
        """List of Executables available on the installation."""

        # System configuration follows
        self.mpiexec = []
        """Path to the system wide (default) mpiexec."""
        self.python = []
        """Path to the python interpreter."""
        self.pbs = None
        """ Resolve class to implement details of particular PBS."""
        JsonData.__init__(self, config)



class ConnectionBase(JsonData):
    """
    Represents connction to a remote machine or local, provides
    hide difference between local and remote
    """
    def __init__(self, config={}):
        self.address=""
        """ IP or hostname"""
        self.uid=""
        """ user id for ssh connection """
        self.password=""
        """ password for ssh connection """
        self.environment = Environment()
        """ Seems that only path to the installation is necesary, possibly path to python."""
        super().__init__(config)

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

    def get_delegator(self, local_service):
        """
        Start delegator and return its proxy.

        We assume that Service itself can behave as ServiceProxy but not vice versa.
        :return: service_proxy
        """
        return local_service

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
            shutil.copyfile(os.path.join(from_prefix, path), os.path.join(to_prefix, path))


class ConnectionSSH(ConnectionBase):


    def __init__(self, config={}):
        """
        :param config:
        :raises SSHAuthenticationError:
        :raises SSHError:
        """
        super().__init__(config)

        self._timeout = 1000
        """timeout for ssh operations"""

        # open ssh connection
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

        try:
            self._ssh.connect(self.address, 22, username=self.uid, password=self.password, timeout=self._timeout)
        except paramiko.AuthenticationException:
            raise SSHAuthenticationError
        except (paramiko.SSHException, socket.error):
            raise SSHError
        except Exception as e:
            logging.error('*** Failed to connect to %s:%d: %r' % (self.address, 22, e))
            raise

        # open an SFTP session
        self._sftp = self._ssh.open_sftp()
        self._sftp.get_channel().settimeout(self._timeout)
        self._sftp_opened = True

        # dict of forwarded local ports, {'local_port': (thread, server)}
        self._forwarded_local_ports = {}

        # delegator proxy
        self._delegator_proxy = None

        # delegator stdin, stdout, stderr
        self._delegator_std_in_out_err = None

    def __del__(self):
        # close all tunels, delagators, etc. immediately
        self.close_connections()

    def is_alive(self):
        """
        Check if SSH connection is still alive.
        :return:
        """
        transport = self._ssh.get_transport()
        if transport.is_active():
            try:
                transport.send_ignore()
                return True
            except EOFError:
                pass
        return False

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
        t.daemon = False
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
            t.setDaemon(True)
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
        for path in paths:
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

    def get_delegator(self, local_service):
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

        if self._delegator_proxy is not None:
            return self._delegator_proxy

        # 1.
        local_port = local_service.repeater._starter_server.address[1]
        remote_port = self.forward_remote_port(local_port)

        # 2.
        child_id = local_service.repeater.add_child()

        # 3.
        try:
            self._delegator_std_in_out_err = self._ssh.exec_command(self.environment.python + " " + os.path.join(self.environment.root, "JobPanel/delegator_service.py") + " {} {} {}".format(child_id, "localhost", remote_port), timeout=self._timeout, get_pty=True)
            #print("/home/radek/.virtualenvs/GeoMop/bin/python /home/radek/work/GeoMop/src/JobPanel/backend/delegator_service.py {} {} {}".format(child_id, "localhost", remote_port))
            #stdin, stdout, stderr = self._ssh.exec_command("sleep 1d", timeout=self._timeout, get_pty=True)
            #print(stdout.readline())
        except paramiko.SSHException:
            raise SSHError
        except socket.timeout:
            raise SSHTimeoutError

        # 4.
        time.sleep(5)

        # 5.
        delegator_proxy = ServiceProxy(local_service.repeater, {}, self)
        delegator_proxy.connect_service(child_id)

        # 6.
        self._delegator_proxy = delegator_proxy

        return delegator_proxy

    def close_connections(self):
        """
        Close al connections in peaceful meaner.
        :param self:
        :return:
        """
        # close all forwarded local ports
        for port in list(self._forwarded_local_ports.keys()):
            self.close_forwarded_local_port(port)

        if self._sftp_opened:
            self._sftp.close()
            self._sftp_opened = False

        self._ssh.close()




