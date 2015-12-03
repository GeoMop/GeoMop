# -*- coding: utf-8 -*-
"""
Unified data structure for presets.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import uuid


class Id:
    @staticmethod
    def get_id():
        return str(uuid.uuid4())


class APreset:
    def __init__(self, name="Default Preset Name"):
        """
        Default initialization.
        :param name: Name of the preset.
        :return: None
        """
        self.name = name
        """Preset name"""

    def get_name(self):
        """
        Default name displayed in UI.
        :return: Name string of the preset.
        """
        return self.name

    def get_description(self):
        """
        Default description displayed in UI.
        (Presets should override this with custom description)
        :return: Custom description string.
        """
        return self.get_name()


class PbsPreset(APreset):
    """
    PBS preset data container.
    """

    def __init__(self, name="Default PBS Preset Name"):
        """
        Default initialization.
        :return: None
        """
        super().__init__(name)
        self.walltime = ""
        """Walltime defines maximum execution time in system"""
        self.nodes = "1"
        """Number of nodes for parallel computations"""
        self.ppn = "1"
        """Processors per node"""
        self.memory = "400mb"
        """Required memory size on node"""
        self.scratch = "400mb"
        """Required disk space size on node"""

    def get_description(self):
        """
        Default description displayed in UI.
        :return: String
        """
        return self.name + ": " + self.walltime


class SshPreset(APreset):
    """
    SSH preset data container.
    """

    def __init__(self, name="Default SSH Preset Name"):
        """
        Default initialization.
        :return: None
        """
        super().__init__(name)
        self.host = "localhost"
        """Host to connect"""
        self.port = "22"
        """Port for connection"""
        self.uid = ""
        """User ID"""
        self.pwd = ""
        """Password"""

    def get_description(self):
        """
        Default description displayed in UI.
        :return: String
        """
        return self.name + ": " + self.host + "; " + self.uid


class ResPreset(APreset):
    """
    Resource preset data container.
    """

    def __init__(self, name="Default Resource Preset Name"):
        """
        Default initialization.
        :return: None
        """
        super().__init__(name)
        # MJ
        self.mj_execution_type = None
        """Defines how to execute MJ"""
        self.mj_ssh_preset = None
        """SSH preset for option"""
        self.mj_remote_execution_type = None
        """Defines how to execute MJ remote component"""
        self.mj_pbs_preset = None
        """PBS preset for option"""
        self.mj_env = None
        """Settings for remote environment"""

        # Job
        self.j_execution_type = None
        """Defines how to execute Job"""
        self.j_ssh_preset = None
        """SSH preset for option"""
        self.j_remote_execution_type = None
        """Defines how to execute Job remote component"""
        self.j_pbs_preset = None
        """PBS preset for option"""
        self.j_env = None
        """Settings for remote environment"""

    def get_description(self):
        """
        Default description displayed in UI.
        :return: String
        """
        return self.name + ": " + str(
            self.mj_execution_type) + " - " + str(
            self.mj_remote_execution_type) + " - " + str(
            self.j_execution_type) + " - " + str(
            self.j_remote_execution_type)


class EnvPreset(APreset):
    """
    Environment preset data container.
    """

    def __init__(self, name="Default Environment Preset Name"):
        """
        Default initialization.
        :return: None
        """
        super().__init__(name)
        # Python environment
        self.python_exec = "python3"
        """Alias or path to python executable"""
        self.scl_enable_exec = None
        """Enable python exec set name over scl"""
        self.module_add = None
        """Module name of required python version"""

        # Libs environment
        self.mpi_scl_enable_exec = None
        """Enable python exec set name over scl"""
        self.mpi_module_add = None
        """Module name required for mpi"""
        self.libs_mpicc = None
        """
        Special location or name for the mpicc compiler wrapper
        used during libs for jobs installation
        (None - use server standard configuration)
        """


class MjPreset(APreset):
    """
    MultiJob preset data container.
    """

    def __init__(self, name="Default MultiJob Preset Name"):
        """
        Default initialization.
        :return: None
        """
        super().__init__(name)
        self.analysis = ""
        """Path to analysis folder"""
        self.resource_preset = None
        """Selected resource preset"""
        self.pbs_preset = None
        """AdHoc PBS preset override"""
        self.log_level = logging.DEBUG
        """Logging level"""
        self.number_of_processes = "1"
        """Number of processes used by MultiJob"""
