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


class PbsPreset(APreset):
    """
    PBS preset data container.
    """

    def __init__(self, **kwargs):
        """
        Default initialization.
        :return: None
        """
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        name = kw_or_def('name', 'Default PBS options name')
        super().__init__(name)
        
        self.pbs_system = kw_or_def('pbs_system')
        """Defines PBS system dialect"""
        self.queue = kw_or_def('queue')
        """Defines preferred queue for execution"""
        self.walltime = kw_or_def('walltime')
        """Walltime defines maximum execution time in system"""
        self.nodes = kw_or_def('nodes')
        """Number of nodes for parallel computations"""
        self.ppn = kw_or_def('ppn')
        """Processors per node"""
        self.memory = kw_or_def('memory')
        """Required memory size on node"""
        self.infiniband = kw_or_def('infiniband', False)
        """infiniband (metacentrum settings)"""

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

    def __init__(self, **kwargs):
        """
        Default initialization.
        :return: None
        """
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        name = kw_or_def('name', 'Default SSH host name')
        super().__init__(name)

        self.host = kw_or_def('host', 'localhost')
        """Host to connect"""
        self.port = kw_or_def('port', '22')
        """Port for connection"""
        self.remote_dir = kw_or_def('remote_dir', 'js_services')
        """Remote directory name"""
        self.uid = kw_or_def('uid', '')
        """User ID"""
        self.pwd = kw_or_def('pwd', '')
        """Password"""
        self.to_pc = kw_or_def('to_pc', True)
        """Remember password on pc"""
        self.to_remote = kw_or_def('to_remote', False)
        """Copy password to remote"""
        self.key = kw_or_def('key', '')
        """Key for password"""
        self.pbs_system = kw_or_def('pbs_system')
        """Defines PBS system dialect"""
        self.env = kw_or_def('env')
        """Settings for remote environment"""

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

    def __init__(self, **kwargs):
        """
        Default initialization.
        :return: None
        """
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        name = kw_or_def('name', 'Default Resource name')
        super().__init__(name)

        # MJ
        self.mj_execution_type = kw_or_def('mj_execution_type')
        """Defines how to execute MJ"""
        self.mj_ssh_preset = kw_or_def('mj_ssh_preset')
        """SSH preset for option"""
        self.mj_remote_execution_type = kw_or_def('mj_remote_execution_type')
        """Defines how to execute MJ remote component"""
        self.mj_pbs_preset = kw_or_def('mj_pbs_preset')
        """PBS preset for option"""

        # Job
        self.j_execution_type = kw_or_def('j_execution_type')
        """Defines how to execute Job"""
        self.j_ssh_preset = kw_or_def('j_ssh_preset')
        """SSH preset for option"""
        self.j_remote_execution_type = kw_or_def('j_remote_execution_type')
        """Defines how to execute Job remote component"""
        self.j_pbs_preset = kw_or_def('j_pbs_preset')
        """PBS preset for option"""

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

    def __init__(self, **kwargs):
        """
        Default initialization.
        :return: None
        """
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        name = kw_or_def('name', 'Default Environment name')
        super().__init__(name)

        # Python environment
        self.python_exec = kw_or_def('python_exec', 'python3')
        """Alias or path to python executable"""
        self.scl_enable_exec = kw_or_def('scl_enable_exec')
        """Enable python exec set name over scl"""
        self.module_add = kw_or_def('module_add')
        """Module name of required python version"""

        # Flow123d runtime
        self.flow_path = kw_or_def('flow_path')
        """Execution path to flow123d"""
        self.pbs_params = kw_or_def('pbs_params', [])
        """PBS parameters for running flow123d"""
        self.cli_params = kw_or_def('cli_params', [])
        """Command line parameters for flow123d"""

