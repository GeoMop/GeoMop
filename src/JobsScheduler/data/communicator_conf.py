# -*- coding: utf-8 -*-
"""
Configuration of communication unit
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
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
        self.walltime = ""
        self.nodes = "1"
        self.ppn = "1"
        self.mem = "400mb"
        self.scratch = "400mb"
        self.with_socket = True  # multijob true; job false
        """Initialize communication over socket"""


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


class ConfigFactory(object):
    @staticmethod
    def get_pbs_config(preset=None, with_socket=True):
        """
        Converts dialog data into PbsConfig instance
        """
        pbs = PbsConfig()
        if preset:
            pbs.name = preset[0]
            # preset[0] is useless description
            pbs.walltime = preset[2]
            pbs.nodes = preset[3]
            pbs.ppn = preset[4]
            pbs.mem = preset[5]
            pbs.scratch = preset[6]
        else:
            pbs.name = None
            pbs.walltime = ""
            pbs.nodes = "1"
            pbs.ppn = "1"
            pbs.mem = "400mb"
            pbs.scratch = "400mb"
        if with_socket:
            pbs.with_socket = with_socket
        return pbs

    @staticmethod
    def get_ssh_config(preset=None):
        """
        Converts dialog data into SshConfig instance
        """
        ssh = SshConfig()
        if preset:
            ssh.name = preset[0]
            # preset[0] is useless description
            ssh.host = preset[2]
            ssh.port = preset[3]
            ssh.uid = preset[4]
            ssh.pwd = preset[5]
        return ssh

    @staticmethod
    def get_env_configs(preset=None, install_job_libs=False,
                        start_job_libs=False):
        """
        Converts dialog data into EnvConfigs instance
        """
        python_env = PythonEnvConfig()
        libs_env = LibsEnvConfig()
        if preset[2]:
            python_env.python_exec = preset[2]
        if preset[3]:
            python_env.scl_enable_exec = preset[3]
        if preset[4]:
            python_env.module_add = preset[4]
        if preset[5]:
            libs_env.mpi_scl_enable_exec = preset[5]
        if preset[6]:
            libs_env.mpi_module_add = preset[6]
        if preset[7]:
            libs_env.libs_mpicc = preset[7]
        libs_env.install_job_libs=install_job_libs
        libs_env.start_job_libs=start_job_libs
        return python_env, libs_env

    @staticmethod
    def get_communicator_config(communicator=None, mj_name=None,
                                log_level=None,
                                preset_type=None):
        """
        Provides preset config for most common communicator types, if you
        provide communicator instance on input with valid preset_type,
        new communicator is derived from original.
        """
        if communicator is None:
            com = CommunicatorConfig(mj_name)
        if communicator is not None:
            com = copy.copy(communicator)
        if mj_name is not None:
            com.mj_name = mj_name
        if log_level is not None:
            com.log_level = log_level
        CommunicatorConfigService.preset_common_type(com, preset_type)
        return com


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

        self.ssh = None
        """Ssh settings class :class:`data.communicator_conf.SshConfig`"""

        self.pbs = None
        """Pbs settings class :class:`data.communicator_conf.PbsConfig`"""

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


class CommunicatorConfigService(object):
    CONF_EXTENSION = ".json"

    @staticmethod
    def save_file(json_file, com):
        data = dict(com.__dict__)
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

    @staticmethod
    def preset_common_type(com, preset_type=None):
        # app
        if preset_type is CommType.app:
            com.communicator_name = CommType.app.value
            com.next_communicator = CommType.multijob.value
            com.output_type = OutputCommType.exec_
        # delegator
        elif preset_type is CommType.delegator:
            com.communicator_name = CommType.delegator.value
            com.next_communicator = CommType.multijob.value
            com.input_type = InputCommType.std
            com.output_type = OutputCommType.exec_
        # mj
        elif preset_type is CommType.multijob:
            com.communicator_name = CommType.multijob.value
            com.next_communicator = CommType.job.value
            com.input_type = InputCommType.socket
            com.output_type = OutputCommType.exec_
        # remote
        elif preset_type is CommType.remote:
            com.communicator_name = CommType.remote.value
            com.next_communicator = CommType.job.value
            com.input_type = InputCommType.std
            com.output_type = OutputCommType.exec_
        # job
        elif preset_type is CommType.job:
            com.communicator_name = CommType.job.value
            com.next_communicator = CommType.none.value
            com.input_type = InputCommType.socket
            com.output_type = OutputCommType.none
        return com
