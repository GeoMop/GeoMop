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
from .pbs import PbsConfig, Pbs
from gm_base.global_const import GEOMOP_INTERNAL_DIR_NAME
from .path_converter import lin2win_conv_path

# import in code
#from .service_base import ServiceStatus

import psutil
import os
import sys
import subprocess
import logging
import re
import time


class Executable(JsonData):
    """
    Data class to collect executable specific informations.
    These data are specific to particular installation.

    This class will be managed for every executed process even for own services of the JobPanel backend.
    """
    def __init__(self, config={}):
        self.name=""
        """ Name of executable. Same accross different installations."""
        self.path=""
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
    def __init__(self, config={}):
        """
        Parameters of particular process.
        """
        self.args = []
        """ Arguments passed to executable."""
        self.secret_args = []
        """Arguments passed to executable, but not saved to service config file."""
        self.pbs_args = PbsConfig()
        """
        Arguments passed to PBS system.
        Reuse data.communicator_conf.PbsConfig, remove dialect, move into PBS module.
        """
        self.mpi_args = []
        """Arguments passed to mpiexec. Do not use."""
        self.work_dir = ""
        """Working directory running process. For stdoutput ... Relative from workspace."""
        JsonData.__init__(self, config)




############################################################################################


class ProcessBase(JsonData):
    """
    Base class defining serializable data of a process.

    Descendants of this class are used to interact with processes:
    - start method: enqueue a process into PBS for execution, exec it, exec it in docker
    - status method: check state of a PBS or other process (queued, running, finished, error)
    - kill method: force terminate running process or delete enqueued process

    A process is started from the delegator when processing request_start_process.
    Stdio and error output are redirected and not porcessed.

    or from a Job (or possibly also from MultiJob). The start method returns a process_id,
    if called from delegator this id is returned back to the parent service
    """
    def __init__(self, process_config):
        self.environment = Environment()
        self.executable = Executable()
        self.exec_args = ExecArgs()
        self.process_id = ""
        self.time_limit = -1.0
        """Limit execution time in seconds, negative value means no limit."""
        self.memory_limit = -1.0
        """Memory limit in MB, negative value means no limit."""
        super().__init__(process_config)

    def _get_limit_args(self):
        """
        Return arguments for limit time and memory.
        :return:
        """
        args = []
        if self.time_limit > 0 or self.memory_limit > 0:
            args.append(self.environment.python)
            args.append(os.path.join(self.environment.geomop_root, "gm_base/exec_with_limit.py"))
            if self.time_limit > 0:
                args.append("-t")
                args.append(str(self.time_limit))
            if self.memory_limit > 0:
                args.append("-m")
                args.append(str(self.memory_limit))
        return args


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
            logging.info("ProcessExec.start()".format())

            args = self._get_limit_args()
            if self.executable.script:
                args.append(self.environment.python)
            if os.path.isabs(self.executable.path):
                args.append(self.executable.path)
            else:
                args.append(os.path.join(self.environment.geomop_root,
                                         self.executable.path))
            args.extend(self.exec_args.args)
            args.extend(self.exec_args.secret_args)
            cwd = os.path.join(self.environment.geomop_analysis_workspace,
                               self.exec_args.work_dir)
            r, w = os.pipe()
            pid = os.fork()
            if pid == 0:
                try:
                    os.close(r)
                    os.setsid()
                    conf_dir = os.path.join(cwd, GEOMOP_INTERNAL_DIR_NAME)
                    os.makedirs(conf_dir, exist_ok=True)
                    with open(os.path.join(conf_dir, "std_out.txt"), 'w') as fd_out:
                        p = psutil.Popen(args, stdout=fd_out, stderr=subprocess.STDOUT, cwd=cwd)
                    os.write(w, "{}@{}".format(p.pid, p.create_time()).encode())
                    os.close(w)
                except:
                    pass
                os._exit(0)
            os.close(w)
            buf = b""
            while True:
                b = os.read(r, 1024)
                if len(b) == 0:
                    break
                buf += b
            os.close(r)
            self.process_id = buf.decode()
            os.waitpid(pid, 0)
            return self.process_id

        def get_status(self, pid_list=None):
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
            if pid_list is None:
                pid_list = [self.process_id]

            ret = {}
            for pid in pid_list:
                r = self._get_status_inner(pid)
                ret[pid] = {"running": r}
            return ret

        def _get_status_inner(self, process_id):
            if process_id == "":
                return False
            pid, create_time = process_id.split(sep="@", maxsplit=1)
            try:
                p = psutil.Process(int(pid))
                if str(p.create_time()) != create_time:
                    # already terminated
                    return False
                status = p.status()
                if status == psutil.STATUS_RUNNING or status == psutil.STATUS_SLEEPING:
                    return True
                else:
                    try:
                        p.wait(timeout=0)
                    except psutil.TimeoutExpired:
                        pass
                    return False
            except psutil.NoSuchProcess:
                # already terminated
                return False
            except psutil.AccessDenied:
                # permission is denied
                assert False

        # def full_state_info(self, pid_list):
        #     """
        #     Full information about the processes.
        #
        #     Currently only a string. Mainly to get further information about some error states in PBS.
        #
        #     :param process_id:
        #     :return:
        #
        #     TODO: Not implement until we know exactly the purpose. Possibly status of the service
        #     may be sufficient, i.e. no qstat call necessary unless user want so or for detailed logging.
        #
        #     """
        #     pass

        def kill(self):
            """
            Kill the process (ID from config).
            :return: True if process was killed.
            """
            if self.process_id == "":
                return True
            pid, create_time = self.process_id.split(sep="@", maxsplit=1)
            try:
                p = psutil.Process(int(pid))
                if str(p.create_time()) != create_time:
                    # already terminated
                    return True
                p.kill()
                p.wait()
                return True
            except psutil.NoSuchProcess:
                # already terminated
                return True
            except psutil.AccessDenied:
                # permission is denied
                return False






class ProcessPBS(ProcessBase):
    """
    Same interface as ProcessExec.

    Reuse: pbs_output_comm.PBSOutputComm._exec, pbs.py, dialects

    TODO: How we incorporate posible advanced PBS functions specific to queued jobs. e.g.
    estimate of start time, target nodes, ...

    Remove checks for dialect and default implementation in pbs.py
    """

    def start(self):
        #self.installation.local_copy_path()

        pbs = Pbs(os.path.join(self.environment.geomop_analysis_workspace,
                               self.exec_args.work_dir),
                  self.exec_args.pbs_args)

        if self.executable.script:
            interpreter = self.environment.python
        else:
            interpreter = None

        if os.path.isabs(self.executable.path):
            command = self.executable.path
        else:
            command = os.path.join(self.environment.geomop_root,
                                   self.executable.path)

        pbs.prepare_file(command, interpreter, [], self.exec_args.args + self.exec_args.secret_args,
                         self._get_limit_args())
        logging.debug("Qsub params: " + str(pbs.get_qsub_args()))
        process = subprocess.Popen(pbs.get_qsub_args(),
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return_code = process.poll()
        if return_code is not None:
            raise Exception("Can not start next communicator " + "python_file" +
                " (return code: " + str(return_code) + ")")
        # wait for jobid
        out = process.stdout.readline()
        job = re.match('(\S+)', str(out, 'utf-8'))
        if job is not None:
            try:
                self.process_id = job.group(1)
            except ValueError:
                jobid = re.match('(\d+)\.', job.group(1))
                if jobid is not None:
                    self.process_id = jobid.group(1)
            logging.debug("Job is queued (id:" + str(self.process_id) + ")")
            # if self.config.with_socket:
            #     i = 0
            #     while(i<1800):
            #         lines = hlp.get_outpup()
            #         time.sleep(1)
            #         if lines is not None and len(lines) >= 2:
            #             lines = hlp.get_outpup()
            #             break
            #         i += 1
            #     self._set_node()
            #     host = re.match( 'HOST:--(\S+)--',  lines[0])
            #     if host is not None:
            #         logger.debug("Next communicator return socket host:" + host.group(1))
            #         self.host = host.group(1)
            #     else:
            #         # try node
            #         if self.node is not None:
            #             self.host = self.node
            #     port = re.match( 'PORT:--(\d+)--', lines[1])
            #     if port is not None:
            #         logger.debug("Next communicator return socket port:" + port.group(1))
            #         self.port = int(port.group(1))
        #self.initialized=True
        return self.process_id

    def get_status(self, pid_list=None):
        if pid_list is None:
            pid_list = [self.process_id]

        ret = {}
        args = ["qstat", "-fx"]
        args.extend(pid_list)
        try:
            output = subprocess.check_output(args,
                                             universal_newlines=True,
                                             timeout=60)
        except subprocess.TimeoutExpired:
            return ret

        # parse output
        lines = output.splitlines()
        for pid in pid_list:
            # find start
            for i in range(len(lines)):
                if lines[i].startswith("Job Id: " + pid):
                    ind_start = i
                    break

            # find end
            ind_end = len(lines)
            for i in range(ind_start + 1, len(lines)):
                if len(lines[i].strip()) == 0:
                    ind_end = i

            # job state
            status = None
            for i in range(ind_start + 1, ind_end):
                s = lines[i].strip()
                if s.startswith("job_state = "):
                    s = s[12:]
                    from .service_base import ServiceStatus
                    if s == "Q":
                        status = ServiceStatus.queued
                    elif s == "R" or s == "E":
                        status = ServiceStatus.running
                    elif s == "F":
                        status = ServiceStatus.done
                    break

            ret[pid] = {"status": status,
                        "raw": "\n".join(lines[ind_start:ind_end])}
        return ret

    def kill(self):
        # todo: Spravne by se melo pockat az se proces ukonci (pomoci qstat), jako u ProcessExec.
        # Ale to by zase dlouho trvalo.
        # Pokud je sluzba ve fronte pbs, tak bude tato implementace fungovat dobre.
        # Problem muze nastat pokud jiz sluzba bezi, ale to s ní zase muzeme komunikovat pres socket
        # a ukoncit ji pres nej.
        try:
            output = subprocess.check_output(["qdel", self.process_id],
                                             universal_newlines=True,
                                             timeout=60,
                                             stderr=subprocess.STDOUT)
            return True
        except subprocess.TimeoutExpired:
            return False
        except subprocess.CalledProcessError:
            return True


class ProcessDocker(ProcessBase):
    """
    Same interface as ProcessExec.

    Used to start backend. Seems there will be always only one backend service.
    In addition we may need a docker configuration data, however try to make
    the docker info (image in particular) part of the installation so accessible through the environment.
    """

    def __init__(self, process_config):
        self.docker_port_expose = ("", 0, 0)
        """Docker port expose (host_interface, host_port, container_port)"""
        self.fterm_path = ""
        """Path to fterm.bat (only used on win)"""
        super().__init__(process_config)

    @staticmethod
    def _is_docker_machine_running():
        try:
            subprocess.check_output(["docker", "ps"], stderr=subprocess.DEVNULL)
        except (OSError, subprocess.CalledProcessError):
            return False
        return True

    def start(self):
        """
        See client_test_py for a docker starting process.
        :return: process_id - possibly hash of the running container.
        """
        # port expose
        arg_p = ""
        if self.docker_port_expose[2] > 0:
            arg_p = str(self.docker_port_expose[2])
            if self.docker_port_expose[1] > 0:
                arg_p = "{}:".format(self.docker_port_expose[1]) + arg_p
            if self.docker_port_expose[0] != "":
                if self.docker_port_expose[1] <= 0:
                    arg_p = ":" + arg_p
                arg_p = self.docker_port_expose[0] + ":" + arg_p

        geomop_root = self.environment.geomop_root
        workspace = self.environment.geomop_analysis_workspace
        cwd = workspace + "/" + self.exec_args.work_dir

        # wrapper
        wrapper_path = geomop_root + "/JobPanel/backend/docker_wrapper.py"
        # if sys.platform == "win32":
        #     wrapper_path = "/" + wrapper_path
        args = [self.environment.python, wrapper_path]

        args.extend(self._get_limit_args())

        if self.executable.script:
            args.append(self.environment.python)

        if self.executable.path.startswith("/"):
            path = self.executable.path
        else:
            path = geomop_root + "/" + self.executable.path
        # if sys.platform == "win32":
        #     path = "/" + path
        args.append(path)

        args.extend(self.exec_args.args)
        args.extend(self.exec_args.secret_args)

        if sys.platform == "win32":
            # start docker machine
            subprocess.check_output(["dockerd.bat"], stderr=subprocess.DEVNULL)
            if not self._is_docker_machine_running():
                time.sleep(1)
                while not self._is_docker_machine_running():
                    time.sleep(1)
                time.sleep(5)

            # flags = "-d"
            # if arg_p != "":
            #     flags += " -p " + arg_p
            # if self.fterm_path != "":
            #     base_args = [self.fterm_path]
            # else:
            #     base_args = ["fterm.bat"]
            # base_args.extend(["--", flags, "/" + cwd])
            base_args = ["docker", "run", "-d"]
            if arg_p != "":
                base_args.extend(["-p", arg_p])
            base_args.extend(["-v", lin2win_conv_path(geomop_root) + ":" + geomop_root,
                              "-v", lin2win_conv_path(workspace) + ":" + workspace,
                              "-w", cwd,
                              "flow123d/3.0.1"])
            output = subprocess.check_output(base_args + args, universal_newlines=True)
            self.process_id = output.strip()
        else:
            #home = os.environ["HOME"]
            uid = os.getuid()
            gid = os.getgid()
            base_args = ["docker", "run", "-d"]
            if arg_p != "":
                base_args.extend(["-p", arg_p])
            base_args.extend(["-v", geomop_root + ":" + geomop_root,
                              "-v", workspace + ":" + workspace,
                              "-w", cwd,
                              "-e", "uid={}".format(uid), "-e", "gui={}".format(gid),
                              "flow123d/3.0.1"])
            # When we want to use ssh keys, it is possible to add following arguments,
            # then keys will be copied to docker.
            # "-e", "home=/mnt//home/radek", "-v", "/home/radek:/mnt//home/radek"
            output = subprocess.check_output(base_args + args, universal_newlines=True)
            self.process_id = output.strip()

        return self.process_id

    def kill(self):
        """
        See client_test.py, BackedProxy.__del__
        :return:
        """
        # if sys.platform == "win32":
        #     args = ["fdocker.bat"]
        # else:
        args = ["docker"]
        args.extend(["rm", "-f", self.process_id])
        try:
            output = subprocess.check_output(args, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass
        return True
