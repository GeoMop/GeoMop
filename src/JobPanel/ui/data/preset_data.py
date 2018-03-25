# -*- coding: utf-8 -*-
"""
Unified data structure for presets.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import uuid
import re
import os

import config
from data import Users


class Id:
    @staticmethod
    def get_id():
        return str(uuid.uuid4())


class APreset:
    re_name = re.compile("^[a-zA-Z0-9]([a-zA-Z0-9]|[_-])*$")

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
        
    def validate(self, excluded, permited):
        """
        validate set data end return dictionary of invalid key, with error
        description
        """
        ret = {}
        if not self.re_name.match(self.name):
            ret["name"]="Bad format of preset name"
        for key, list in excluded.items():
            variable = getattr(self, key)
            if variable in list:
                ret[key]="Value '{0}' is already in use".format(key)
        for key, list in permited.items():
            variable = getattr(self, key)
            if variable not in list:
                ret[key]="Variable's '{1}' value '{0}'  is not in permited values".format(
                    variable, key)        
        return ret

    def __repr__(self):
        """
        Representation of object
        :return: String representation of object.
        """
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)

    def mangle_secret(self):
        """
        Mangles secret data.
        :return:
        """
        pass

    def demangle_secret(self):
        """
        Demangles secret data.
        :return:
        """
        pass


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
        
    def validate(self, excluded, permited):
        """
        validate set data end return dictionary of invalid key, with error
        description
        :param excluded: Is dictionary of lists excluded values for set key.
        :param permited: Is dictionary of lists permited values for set key.
        """
        ret = super().validate(excluded, permited)       
        if not re.match("^$|(\d+[wdhms])(\d+[dhms])?(\d+[hms])?(\d+[ms])?(\d+[s])?", self.walltime):
            ret["walltime"]="Bad format of walltime"
        if not re.match("^$|\d+(mb|gb)", self.memory):
            ret["memory"]="Bad format of memory"
        return ret


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
        self.geomop_root = kw_or_def('geomop_root', '')
        """Remote GeoMop root"""
        self.workspace = kw_or_def('workspace', '')
        """Remote analysis workspace"""
        self.uid = kw_or_def('uid', '')
        """User ID"""
        self.pwd = kw_or_def('pwd', '')
        """Password"""
        self.to_pc = kw_or_def('to_pc', True)
        """Remember password on pc"""
        self.to_remote = kw_or_def('to_remote', False)
        """Copy password to remote"""
        self.use_tunneling = kw_or_def('use_tunneling', False)
        """Communication is switch to socket over ssh tunnel"""
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
        
    def validate(self, excluded, permited):
        """
        validate set data end return dictionary of invalid key, with error
        description
        :param excluded: Is dictionary of lists excluded values for set key.
        :param permited: Is dictionary of lists permited values for set key.
        """
        valid_addr = re.compile(
            "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
        valid_host = re.compile(
            "^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        ret = super().validate(excluded, permited)
        if not valid_addr.match(self.host):
            if not valid_host.match(self.host):
                ret["host"]="Invalid ssh dns name or ip address"
        elif len(self.host)>63:
            ret["host"]="Invalid dns name (too long)" 
        if not isinstance(self.port, int) or self.port<1 or self.port>65535:
            ret["port"]="Invalid ssh port"     
        # todo: spravit, taky pridat validaci pro workspace
        # if not self.re_name.match(self.geomop_root):
        #     ret["geomop_root"]="Bad format of remote directory"
        if self.uid is None and len(self.uid)==0:
            ret["uid"]="Bad format of ssh user name"            
        return ret
        
    def mangle_secret(self):
        """
        Mangles secret data.
        :return:
        """
        from ui.imports.workspaces_conf import BASE_DIR
        self.key = Users.save_reg(self.name, self.pwd, os.path.join(config.__config_dir__, BASE_DIR))
        self.pwd = "a124b.#"

    def demangle_secret(self):
        """
        Demangles secret data.
        :return:
        """
        from ui.imports.workspaces_conf import BASE_DIR
        pwd = Users.get_reg(self.name, self.key, os.path.join(config.__config_dir__, BASE_DIR))
        if pwd is not None:
            self.pwd = pwd
        else:
            self.pwd = ""


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
