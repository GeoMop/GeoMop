import shutil
import os
import os.path

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

    def __init__(self, config):
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
    def __init__(self, config):
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
    def __init__(self, config):
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
        by 'remote_prefix' for destination. Directories are uploaded recursively.
        If target exists, raise appropriate exception (...?)
        :return: None

        Implementation: just copy
        """
        self._copy(paths, local_prefix, remote_prefix)


    def download(self, paths, local_prefix, remote_prefix):
        """
        Download given relative 'paths' to remote, prefixing them by 'local_prefix' for destination and
        by 'remote_prefix' for source. Directories are downloaded recursively.
        If target exists, raise appropriate exception.
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



    def _copy(self, paths, strip_path, prefix_path):
        if (not os.path.isabs(prefix_path)):
            prefix_path = os.path.join(self.workspace, prefix_path)

        if (strip_path == prefix_path):
            return
        for src in paths:
            rel_src=os.path.relpath(path, strip_path)
            assert( rel_src[0:3] != "../")
            dst=os.path.join(prefix_path, rel_src)
            # Assumes that target directory does not exist,
            # files should be overwritten. We may copy and modify the source
            shutil.copytree(src, dst)


class ConnectionSSH(ConnectionBase):


    def __init__(self, config):
        super().__init__(config)
        # here we should open ssh connection

    def __del__(self):
        # close all tunels, delagators, etc. immediately

    def forward_local_port(self, remote_port):
        """
        Get free local port and open SSH tunel for forwarding connection
        to the local port to the given 'remote port'.
        :param remote_port:
        :return: local_port
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
        pass

    def upload(self, paths, local_prefix, remote_prefix):
        """
        Upload given 'paths' to remote stripping 'local_prefix' and
        replacing it with 'remote_prafix'. If remote_prefix is relative it is prefixed with
        remote workspace. Directories are uploaded recursively.
        If target exists, raise appropriate exception.
        :return: None

        Implementation: just copy
        """
        pass

    def download(self, paths, local_prefix, remote_prefix):
        """
        Download given 'paths' from remote stripping 'strip_path' and
        replacing it with 'prefix_path'. If prefix path is relative it is prefixed with
        remote workspace. Directories are uploaded recursively. If target exists, raise appropriate exception.
        :return: None

        Implementation: just copy
        """
        pass

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
        pass




