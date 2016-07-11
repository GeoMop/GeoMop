# -*- coding: utf-8 -*-
"""
Configuration of communication unit
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import json
import logging
import os
from enum import Enum, IntEnum


class OutputCommType(IntEnum):
    """Severity of an error."""
    none = 0
    ssh = 1
    exec_ = 2
    pbs = 3


class InputCommType(IntEnum):
    """Severity of an error."""
    none = 0
    std = 1
    socket = 2
    pbs = 3


class CommType(Enum):
    """Types of communicators"""
    none = ""
    app = "app"
    delegator = "delegator"
    remote = "remote"
    multijob = "mj_service"
    job = "job"


class PbsConfig(object):
    """
    Class for configuration qsub command
    """

    def __init__(self):
        """init"""
        self.name = None
        """name as unique job identifier for files"""
        self.dialect = None
        self.queue = None
        self.walltime = None
        self.nodes = "1"
        self.ppn = "1"
        self.memory = None
        self.scratch = None
        self.with_socket = True
        """
        Initialize communication over socket, True in case of MultiJob
        otherwise False.
        """
        self.pbs_params = []

class PathsConfig(object):
    """
    Class for configuration data, config, logs and locks paths
    
    self.app_dir variable is for renaming app directory created in remote.
    Other path is for communicators running on client pc. For communicators
    on remote pc (after first SSH connection) should be empty. First  
    communicator before SSH should have self.copy_ex_libs set.    
    """

    def __init__(self):
        """init"""
        self.app_dir = "js_services"
        """Name of application directory for remote"""
        self.home_dir = None
        """Absolut path to directory for central-log, locks and versions subdirectories.
        If variable is None, app directory is use"""
        self.work_dir = None
        """Absolut path to directory for result subdirectory.
        If variable is None, app directory/jobs/'JOB_NAME' path is use"""
        self.ex_lib_path = None
        """if absolute paths is set, is added to communicatin sys.path, if
        is None, path to lib directory is added"""
        self.copy_ex_libs = []
        """
        This variable contain relative directories with client system sepparators 
        from self.ex_lib_path. (if self.ex_lib_path is None, variable is ignored) This
        directories is copy to lib directory on remote.
        """


class SshConfig(object):
    """
    Class for ssh configuration
    """

    def __init__(self):
        """init"""
        self.name = None
        self.host = "localhost"
        self.port = "22"
        self.uid = ""
        self.pwd = ""
        self.to_pc = True
        """password is store in computer"""
        self.to_remote = False
        """password is store in remote"""
        self.key = False

class PythonEnvConfig(object):
    """
    Class for python environment configuration
    """

    def __init__(self):
        """init"""
        self.python_exec = "python3"
        self.scl_enable_exec = None
        """Enable python exec set name over scl"""
        self.module_add = None


class LibsEnvConfig(object):
    """
    Class for libs environment configuration
    """

    def __init__(self):
        """init"""
        self.mpi_scl_enable_exec = None
        """Enable python exec set name over scl"""
        self.mpi_module_add = None

        self.libs_mpicc = None
        """
        special location or name for the mpicc compiler wrapper
        used during libs for jobs installation (None - use server
        standard configuration)
        """

        self.install_job_libs = False
        """Communicator will install libs for jobs"""

        self.start_job_libs = False
        """Communicator will prepare libs for job running"""


class CommunicatorConfig(object):
    """
    CommunicatorConfiguration contains data for initialization
    :class:`communication.communicator.Communicator` class. This data is
    serialized by gui application and save as file for later loading by
    :class:`communication.communicator.Communicator`.
    """

    def __init__(self, mj_name=None):
        self.communicator_name = CommType.none.value
        """this communicator name for login file, ..."""

        self.next_communicator = CommType.none.value
        """communicator file that will be start"""
        
        self.direct_communication = False
        """
        This parameter is for remote and mj_service configurator.
        If parametr is true, this communicators comunicate directli 
        over socket. Only installation message is sent over remote.        
        """
        
        self.central_log = False
        """Application log to centrall log"""

        self.input_type = InputCommType.none
        """Input communication type"""

        self.output_type = OutputCommType.none
        """Output communication type"""

        self.mj_name = mj_name
        """folder name for multijob data"""

        self.port = 5723
        """
        First port for the socket communication with this communicator.
        If this port has the use of another application, socket connection
        is set to next port in order.
        """

        self.log_level = logging.WARNING
        """log level for communicator"""

        self.number_of_processes = 1
        """ Number of processes in multijob or job, everywhere else is 1"""

        self.paths_config = PathsConfig()
        """paths to directory structure datas"""

        self.ssh = None
        """Ssh settings class :class:`data.communicator_conf.SshConfig`"""

        self.pbs = None
        """Pbs settings class :class:`data.communicator_conf.PbsConfig`"""
        
        self.app_version = None
        """
        Applicationj version. If version in remote installation is different
        new instalation is created
        """
        
        self.conf_long_id = None
        """
        Long id of configuration. If  in remote installation is different
        id new configuration is reloaded
        """

        self.python_env = None
        """
        Python environment settings class
        :class:`data.communicator_conf.PythonEnvConfig`
        """

        self.libs_env = None
        """
        Python environment settings class
        :class:`data.communicator_conf.PythonEnvConfig`
        """

        self.flow_path = None
        """Execution path to flow123d"""

        self.cli_params = []
        """Command line parameters for flow123d"""


class CommunicatorConfigService(object):
    CONF_EXTENSION = ".json"

    @staticmethod
    def save_file(json_file, com):
        data = dict(com.__dict__)
        data["paths_config"] = com.paths_config.__dict__
        if data["ssh"]:
            data["ssh"] = com.ssh.__dict__
        if data["pbs"]:
            data["pbs"] = com.pbs.__dict__
        if data["python_env"]:
            data["python_env"] = com.python_env.__dict__
        if data["libs_env"]:
            data["libs_env"] = com.libs_env.__dict__
        json.dump(data, json_file, indent=4, sort_keys=True)

    @staticmethod
    def load_file(json_file, com=CommunicatorConfig()):
        data = json.load(json_file)
        paths_config = PathsConfig()
        if data["paths_config"]:
            paths_config.__dict__ = data["paths_config"]
        data["paths_config"] = paths_config   
        if data["ssh"]:
            ssh = SshConfig()
            ssh.__dict__ = data["ssh"]
            data["ssh"] = ssh
        if data["pbs"]:
            pbs = PbsConfig()
            pbs.__dict__ = data["pbs"]
            data["pbs"] = pbs
        if data["python_env"]:
            python_env = PythonEnvConfig()
            python_env.__dict__ = data["python_env"]
            data["python_env"] = python_env
        if data["libs_env"]:
            libs_env = LibsEnvConfig()
            libs_env.__dict__ = data["libs_env"]
            data["libs_env"] = libs_env
        com.__dict__ = data

    @staticmethod
    def get_file_path(conf_path, com_type):
        filename = com_type + CommunicatorConfigService.CONF_EXTENSION
        return os.path.join(conf_path, filename)
