"""
Various ways how to start a service from the same machine.

We should have a testing mechanism of ProcessExec and ProcessPBS classes.
Tests are used both for unit testing and for testing configuration of the system.
We need:
- Mockup MPI application 'mpi_testapp' (using PyMPI) that can:
    - run in parallel for given time.
    - exchange some MPI message to test MPI works
    - simulate error in single process

- Jenkins should connect to Metacentrum an execute the PBS tests there

Tests:
- Start 'mpi_testapp' in serial, simulate error. Test that get_states works (running, error).
- Start 'mpi_testapp' in parallel, simulate error (in single process). Test that all processes stop.
- Start 'mpi_testapp' in parallel, kill the process (?? master). Test that all processes stop.
- Similar for PBS + test reporting 'queued' state.

"""


class Executable(JsonData):
    """
    Data class to collect executable specific informations.
    These data are specific to particular installation.

    This class will be managed for every executed process even for own services of the JobPanel backend.
    """
    def __init__(self, config):
        self.name=""
        """ Name of executable. Same accross different installations."""
        self.path=[]
        """ Path to executable in particular installation."""
        self.mpiexec_path=""
        """ Optional executable specific mpiexec. Default is to use systemwide mpiexec."""
        self.modules=[]
        """ Modules that executable depends on."""

        self.script=False
        """If executable is python script."""
        self.mpi_parallel=False
        """
        If executable is MPI parallel (can be executed by mpiexec).
        Can be turned off by test_executable.
        """
        self.test_args=[]
        """Arguments to test executable. Test should be short and finish with success."""
        self.works=False
        """Is set by Installation.test_executable."""
        JsonData.__init__(self, config)

# qsub pbs_options mpirun

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


    def test_installation(self):
        """
        Test all executables, find executables ...
        Try to use already filled data.
        :return:
        """

    def exec(self, executable_name, args):
        """
        Execute executable (possibly with mpiexec), wait for finish.
        Raise exception on abnormal return code.
        :param executable_name: name of executable to run
        :param args: ExecArgs
        :return: (StdOut, StdErr)
        """

    def test_executable(self, executable_name):
        """
        Test if executable works in current installation and if it
        works with mpiexec.
        Set flags: mpi_parallel,
        :param executable_name:
        :return:
        """
        pass

    def exec_persistent(self, executable, arg):
        """
        Start given executable in a new persistent process.
        Load correct modules, can run only scripts and only without mpi.
        Is used to start services.

        :param executable: Executable
        :param parameters: ProcessParameters
        :return: process_id - string that identify the process on the same machine
        """

    def kill_persistent(self, process_id):
        """
        Kill process with given ID.
        :return: True if process was killed.
        """
        pass



"""
Backend life cycle

# Assuming we have image
# Starting
1. listen at starting port
2. start service in the docker

starting_host = {
    __class__ = Local
    environment = {
        install_path
        ... optional, default
        }
    }

exec_method = {
    __class__ = docker
    docker_image
    }

executable = "service.py" # name reference into environment
exec_args = "-p <docker_host_address>:<port>"

3. service open listening port
4. service connects to the parent starting port,
   send own addres:port,
   wait for confirm, stop after timeout
5. parent confirms, and close connection
6. parent connects to listening port of child service
7. parent sends service config data, or its actualization:

service_data = {
    __class__ = (service type ??
    # get from cmd line
    parent_host
    parent_starting_port

    # filled by child service and possibly improtant for parent service
    running_host
    listenning_port

    # get from installation
    environment

    # from cmd line or from file, if it turns upt that initial connection takes over 1s
    first_request

    # get from parent after start
    exec_method
    environment (update)
}

process requests:
- (resend messages)
- upload files to remote
- start MJ
- stop MJ (send stop and kill after timeout)
- download files

- clean on remote



# Data that must be passed to the service script through a file or through connection





Data for Job, MJ,  execution.

starting_host = {
    __class__ = ( Ssh | Local )
    IP or DSN
    uid
    pass
    environment = {
        install_path
        ... optional, default
        }
    }

exec_method = {
    __class__ = ( popen, pbs, docker )
    # generic
    walltime
    memory
    n_proc
    # pbs specific
    queue
    ppn
    }

executable = "" # name reference into environment
exec_args = ""

# Data that must be passed to the service script through a file or through connection
service_data = {
    __class__ = (service type ??
    exec_method
    environment

    parent_host
    parent_starting_port

    first_request


    # filled by job and possibly improtant for parent service
    running_host
    listenning_port
}

"""


class ServiceStarterBase(JsonData):
    def __init__(self, environment):
        self.environment=Environment()
        self.environment
        super().__init__(config)

class ServiceStarterExec(ProcessBase):
    """
    Operate with persistent process.
    """
    def exec(self, executable, exec_args):
        """
        Start executable provided in configuration.

        :param executable:
        :param exec_args:
        :return: Process id, serializable object unique on this machine.
        Implementation: same as in current exec, or with double fork
        """
        pass

    def kill(self, process_id):
        """
        Kill given process.
        :param process_id:
        :return:
        """
        pass

class ServiceStarterPBS(ProcessBase):
    def exec(self, executable, exec_args):
        """
        Start executable provided in configuration.
        :return: Process id, serializable object unique on this machine.

        Implementation: start using pbs with
        """

    def kill(self, process_id):
        """
        Kill given job.

        :param process_id:
        :return:
        """
        pass


class ServiceStarterDocker(ProcessBase):
    def exec(self, executable, exec_args):
        """
        Start executable provided in configuration.
        :return: Process id, serializable object unique on this machine.

        Implementation: start using pbs with
        """
        pass

    def kill(self, process_id):
        """
        Kill given job.

        :param process_id:
        :return:
        """
        pass


############################################################################################
    ########################################################################




    class ProcessExec(JsonData):
        """
        Class for starting a persistent process.
        Constructor inherited.

        How to get return code of the persistent process in order to report error state?

        Should be able to furhter monitor that process is running and
        able to kill it.
        """

        def start(self, executable, parameters):
            """
            Start given executable in a new persistent process.
            Load correct modules, use mpiexec to start parallel processes.

            :param executable: Executable
            :param parameters: ProcessParameters
            :return: process_id - string that identify the process on the same machine
            """
            pass

        def get_states(self, pid_list):
            """
            Get states of running processes.
            Idea is to get all available states at once since 'qstat' have high latency.

            Reuse and reduce states.TaskStatus enum.
            Use 'ps' to get all processes running by the user, filter only given pids.
            We want to

            :return: [ (process_id, process_state), ... ]
            """

        def full_state_info(self, pid_list):
            """
            Full information about the processes.

            Currently only a string. Mainly to get further information about some error states in PBS.

            :param process_id:
            :return:
            """
            pass

        def kill(self, process_id):
            """
            Kill process with given ID.
            :return: True if process was killed.
            """
            pass

    class ProcessPBS(JsonData):
        """
        Same interface as ProcessExec.

        Reuse: pbs_output_comm.PBSOutputComm._exec, pbs.py, dialects

        How we incorporate posible advanced PBS functions specific to queued jobs. e.g.
        estimate of start time, target nodes, ...

        Remove checks for dialect and default implementation in pbs.py
        """
        pass