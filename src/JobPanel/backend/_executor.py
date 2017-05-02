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
from .json_data import JsonData
from .environment import Environment

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


class ExecArgs(JsonData):
    def __init__(self, config):
        """
        Parameters of particular process.
        """
        self.args = []
        """ Arguments passed to executable."""
        self.pbs_args = PbsConfig()
        """
        Arguments passed to PBS system.
        Reuse data.communicator_conf.PbsConfig, remove dialect, move into PBS module.
        """
        self.mpi_args = []
        """Arguments passed to mpiexec. Do not use."""
        JsonData.__init__(self, config)








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


"""





############################################################################################


class ProcessBase(JsonData):
    """
    Base class defining serializable data of a process.

    Descendants of this class are used to interact with processes:
    - start method: enqueue a process into PBS for execution, exec it, exec it in docker
    - status method: check state of a PBS or other process (queued, running, finished, error)
    - kill method: force terminate running process or delete enqueued process

    A process is started either from the delegator when processing request_start_process
    or from a Job (or possibly also from MultiJob). The start method returns a process_id,
    if called from delegator this id is returned back to the parent service
    """
    def __init__(self, process_config):
        self.environment = Environment()
        self.executable = Executable()
        self.exec_args = ExecArgs()
        self.proces_id = ""
        super().__init__(process_config)


class ProcessExec(ProcessBase):
        """
        Class for starting a local persistent process.
        Constructor inherited.

        TODO: How to get return code of the persistent process in order to report error state?

        Should be able to furhter monitor that process is running and
        able to kill it.

        Implementation: same as in ExecOutputComm.exec, or with double fork
        """


        def start(self):
            """
            Start given executable in a new persistent process.
            Load correct modules, use mpiexec to start parallel processes.

            :param executable: Executable
            :param parameters: ProcessParameters
            :return: process_id - object that identify the process on the same machine
            """
            pass

        def get_status(self, pid_list):
            """
            Get states of running processes.
            Idea is to get all available states at once since 'qstat' have high latency.

            Reuse and reduce states.TaskStatus enum.
            Use 'ps' to get all processes running by the user, filter only given pids.
            We want to

            :return: [ (process_id, process_state), ... ]

            TODO: Not implement until we know exactly the purpose. Possibly status of the service
            may be sufficient, i.e. no qstat call necessary unless user want so or for detailed logging.
            """

        def full_state_info(self, pid_list):
            """
            Full information about the processes.

            Currently only a string. Mainly to get further information about some error states in PBS.

            :param process_id:
            :return:

            TODO: Not implement until we know exactly the purpose. Possibly status of the service
            may be sufficient, i.e. no qstat call necessary unless user want so or for detailed logging.

            """
            pass

        def kill(self):
            """
            Kill the process (ID from config).
            :return: True if process was killed.
            """
            pass






class ProcessPBS(ProcessBase):
    """
    Same interface as ProcessExec.

    Reuse: pbs_output_comm.PBSOutputComm._exec, pbs.py, dialects

    TODO: How we incorporate posible advanced PBS functions specific to queued jobs. e.g.
    estimate of start time, target nodes, ...

    Remove checks for dialect and default implementation in pbs.py
    """
    pass


class ProcessDocker(ProcessBase):
    """
    Same interface as ProcessExec.

    Used to start backend. Seems there will be always only one backend service.
    In addition we may need a docker configuration data, however try to make
    the docker info (image in particular) part of the installation so accessible through the environment.
    """

    def start(self):
        """
        See client_test_py for a docker starting process.
        :return: process_id - possibly hash of the running container.
        """
        pass

    def kill(self):
        """
        See client_test.py, BackedProxy.__del__
        :return:
        """
        pass