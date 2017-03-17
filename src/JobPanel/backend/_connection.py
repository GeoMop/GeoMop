from .json_data import JsonData

import paramiko

import shutil
import os
import os.path
import threading

import select
import socket
import socketserver


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
        self.workspace=""
        """ Absolute path to the workspace """
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

        Implementation: just copy
        """
        self._copy(paths, local_prefix, remote_prefix)


    def download(self, paths, local_prefix, remote_prefix):
        """
        Download given relative 'paths' to remote, prefixing them by 'local_prefix' for destination and
        by 'remote_prefix' for source.
        If target exists, replace it.
        :return: None

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
        if not os.path.isabs(to_prefix):
            to_prefix = os.path.join(self.workspace, to_prefix)

        if from_prefix == to_prefix:
            return
        for path in paths:
            shutil.copy(os.path.join(from_prefix, path), os.path.join(to_prefix, path))


g_verbose = False
def verbose(s):
    if g_verbose:
        print(s)


class ConnectionSSH(ConnectionBase):


    def __init__(self, config={}):
        super().__init__(config)

        # open ssh connection
        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        self._ssh.set_missing_host_key_policy(paramiko.WarningPolicy())

        try:
            self._ssh.connect(self.address, 22, username=self.uid, password=self.password)
        except Exception as e:
            verbose('*** Failed to connect to %s:%d: %r' % (self.address, 22, e))
            raise

        # open an SFTP session
        self._sftp = self._ssh.open_sftp()

        # server list
        self._servers = []

    def __del__(self):
        # close all tunels, delagators, etc. immediately
        self.close_connections()

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
                try:
                    chan = self.ssh_transport.open_channel('direct-tcpip',
                                                           ("localhost", remote_port),
                                                           self.request.getpeername())
                except Exception as e:
                    verbose('Incoming request to %s:%d failed: %s' % ("localhost",
                                                                      remote_port,
                                                                      repr(e)))
                    return
                if chan is None:
                    verbose('Incoming request to %s:%d was rejected by the SSH server.' %
                            ("localhost", remote_port))
                    return

                verbose('Connected!  Tunnel open %r -> %r -> %r' % (self.request.getpeername(),
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
                verbose('Tunnel closed from %r' % (peername,))

        # port 0 means to select an arbitrary unused port
        server = ForwardServer(('', 0), Handler)
        ip, local_port = server.server_address
        self._servers.append(server)

        # start server in thread
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()

        return local_port

    def forward_remote_port(self, local_port):
        """
        Get free remote port and open SSH tunel for forwarding connection
        from a remote port to the given 'local_port'.
        :param local_port:
        :return: remote_port
        """

        def handler(chan, origin, server):
            def inner_handler():
                sock = socket.socket()
                try:
                    sock.connect(("localhost", local_port))
                except Exception as e:
                    verbose('Forwarding request to %s:%d failed: %r' % ("localhost", local_port, e))
                    return

                verbose('Connected!  Tunnel open %r -> %r -> %r' % (chan.origin_addr,
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
                verbose('Tunnel closed from %r' % (chan.origin_addr,))

            t = threading.Thread(target=inner_handler)
            t.setDaemon(True)
            t.start()

        remote_port = self._ssh.get_transport().request_port_forward('', 0, handler)
        return remote_port

    def upload(self, paths, local_prefix, remote_prefix):
        """
        Upload given relative 'paths' to remote, prefixing them by 'local_prefix' for source and
        by 'remote_prefix' for destination.
        If target exists, replace it.
        :return: None

        Implementation: just copy
        """
        for path in paths:
            self._sftp.put(os.path.join(local_prefix, path), os.path.join(remote_prefix, path))

    def download(self, paths, local_prefix, remote_prefix):
        """
        Download given relative 'paths' to remote, prefixing them by 'local_prefix' for destination and
        by 'remote_prefix' for source.
        If target exists, replace it.
        :return: None

        Implementation: just copy
        """
        for path in paths:
            self._sftp.get(os.path.join(remote_prefix, path), os.path.join(local_prefix, path))

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
        for server in self._servers:
            server.shutdown()
            server.server_close()
        self._sftp.close()
        self._ssh.close()




