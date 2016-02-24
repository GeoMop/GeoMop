# -*- coding: utf-8 -*-
"""
Unified data structure for presets.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
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

    def __repr__(self):
        """
        Representation of object
        :return: String representation of object.
        """
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    @staticmethod
    def clone(prototype):
        """Create a new instance from the given prototype.

        This function is used as a workaround for using YAML loaded presets. Because
        YAML doesn't call __init__, any update and change in config presents a problem.
        Using the cloning function solve this.
        """
        clone = type(prototype)()  # create a new instance of the same type
        clone.__dict__.update(prototype.__dict__)  # copy the data
        return clone


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
        self.dialect = None
        """Defines PBS system"""
        self.queue = None
        """Defines preferred queue for execution"""
        self.walltime = None
        """Walltime defines maximum execution time in system"""
        self.nodes = None
        """Number of nodes for parallel computations"""
        self.ppn = None
        """Processors per node"""
        self.memory = None
        """Required memory size on node"""
        self.scratch = None
        """Required disk space size on node"""

    def get_description(self):
        """
        Default description displayed in UI.
        :return: String
        """
        return self.name + ": " + str(self.walltime)


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

        # Flow123d runtime
        self.flow_path = None
        """Execution path to flow123d"""
        self.pbs_params = []
        """PBS parameters for running flow123d"""
        self.cli_params = []
        """Command line parameters for flow123d"""

