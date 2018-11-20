from .json_data import JsonData


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

        GUI side: Environment configuration should be part of
        connection as it is related to particular machine. Still allowing to
        copy the  connection to new one reusing environment or ssh. Environment setup should be minimalistic
        by default just setting workspace and root dir of GeoMop installation.

        SSH connection test should perform test both test of SSH connection as well as test of installation
        this fill rest of environment and allows to modify invalid setting (mpi, python, etc.)
        Possible problems can be resolved by user manually and further tested in the Connection panel.
    """

    def __init__(self, config={}):
        """
        If config have 'version_id' we just check that it match
        the version installed at 'root'. Otherwise we start test_installation.
        :param config: InstallationData
        """
        self.geomop_root = ""
        """
        Path to the root directory of the GeoMop backend installtion.
        The only attribute that must be provided by user.
        """
        self.geomop_analysis_workspace = ""
        """Path to the workspace root"""
        self.version_id = ""
        """ Version ID of the installation. This is set by 'test_installation'
        and checked against true state of the installation in constructor."""
        self.executables = []
        """List of Executables available on the installation."""

        # System configuration follows
        self.mpiexec = ""
        """Path to the system wide (default) mpiexec."""
        self.python = ""
        """Path to the python interpreter."""
        self.pbs = ""
        """ Resolve class to implement details of particular PBS."""
        JsonData.__init__(self, config)
