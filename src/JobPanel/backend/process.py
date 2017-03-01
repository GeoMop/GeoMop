"""
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

class JsonData:
    """
    Abstract base class for various data classes.
    These classes are basically just documented dictionaries,
    which are JSON serializable and provide some syntactic sugar
    (see DotDict from Flow123d - Jan Hybs)
    In order to simplify also serialization of non-data classes, we
    should implement serialization of __dict__.

    Why use JSON for serialization? (e.g. instead of pickle)
    We want to use it for both sending the data and storing them in files,
    while some of these files should be human readable/writable.

    Move to own module. ?? Anything similar in current JobPanel?
    """
    def __init__(self, config):
        """
        Initialize class dict from config serialization.
        :param config:
        """
    pass


class Executable(JsonData):
    """
    Data class to collect executable specific informations.
    These data are specific to particular installation.
    """
    name=""
    """ Name of executable. Same accross different installations."""
    path=[]
    """ Path to executable in particular installation."""
    mpi_parallel=True
    """ If executable is MPI parallel (can be executed by mpiexec)."""
    mpiexec_path=""
    """ Optional executable specific mpiexec. Default is to use systemwide mpiexec."""
    modules=[]
    """ Modules that executable depends on."""
    pass







class ProcessParameters(JsonData):
    """
    Parameters of particular process.
    """
    args=[]
    """ Arguments passed to executable."""
    pbs_args=PbsConfig()
    """
    Arguments passed to PBS system.
    Reuse data.communicator_conf.PbsConfig, remove dialect, move into PBS module.
    """
    mpi_args=[]
    """Arguments passed to mpiexec. Do not use."""


class SystemConfig(JsonData):
    """
    Various system specific data.
    """
    pbs_dialect="Default"
    """ Resolve class to implement details of particular PBS."""


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