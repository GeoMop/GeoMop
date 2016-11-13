# -*- coding: utf-8 -*-
"""
JobPanel data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os

import config as cfg
from geomop_util import Serializable

from .preset_data import EnvPreset, PbsPreset, ResPreset, SshPreset
from .mj_data import MultiJob
from ui.imports.workspaces_conf import WorkspacesConf, BASE_DIR
from geomop_analysis import Analysis

class PersistentDict(dict):
    """Persistent dictionary containing configuration."""

    @staticmethod
    def open(cls, id=None):
        directory = os.path.join(BASE_DIR, cls.DIR)
        fn = cls.FILE_NAME
        if id is not None:
            fn += "_" + str(id)
        config = cfg.get_config_file(fn, directory, cls=cls)
        if config is None:
            config = cls()
        return config

    def save(self, id=None):
        directory = os.path.join(BASE_DIR, self.DIR)
        fn = self.FILE_NAME
        if id is not None:
            fn += "_" + str(id)
        cfg.save_config_file(fn, self, directory)


class MultiJobData(PersistentDict):
    """
    Child class for MJ data.
    """
    DIR = "mj"
    FILE_NAME = "mj"

    __serializable__ = Serializable(
        composite={'__all__': MultiJob}
    )

    @staticmethod
    def open(id, path):
        mjs = PersistentDict.open(MultiJobData, id)
        if path is not None:
            for key in mjs:
                dir = os.path.join(path, mjs[key].preset.analysis, 'mj', mjs[key].preset.name)
                if  not os.path.isdir(dir):
                    mjs[key].valid = False            
        return mjs
     
    def save(self, id):
        super(MultiJobData, self).save(id)


class SshData(PersistentDict):
    """
    Child class for SSH data.
    """
    DIR = "ssh"
    FILE_NAME = "ssh"

    __serializable__ = Serializable(
        composite={'__all__': SshPreset}
    )

    @staticmethod
    def open():
        return PersistentDict.open(SshData)


class PbsData(PersistentDict):
    """
    Child class for PBS data.
    """
    DIR = "pbs"
    FILE_NAME = "pbs"

    __serializable__ = Serializable(
        composite={'__all__': PbsPreset}
    )

    @staticmethod
    def open():
        return PersistentDict.open(PbsData)


class ResourcesData(PersistentDict):
    """
    Child class for RES data.
    """
    DIR = "resources"
    FILE_NAME = "resources"

    __serializable__ = Serializable(
        composite={'__all__': ResPreset}
    )

    @staticmethod
    def open():
        return PersistentDict.open(ResourcesData)


class EnvPresets(PersistentDict):
    """
    Child class for ENV data.
    """
    DIR = "environments"
    FILE_NAME = "environments"

    __serializable__ = Serializable(
        composite={'__all__': EnvPreset}
    )

    @staticmethod
    def open():
        return PersistentDict.open(EnvPresets)


class ConfigData:
    """
    Child class for Config data.
    """
    DIR = "settings"
    FILE_NAME = "settings"

    __serializable__ = Serializable(
        excluded=['observers']
    )

    def __init__(self, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        self.observers = []
        """List of observer objects to be notified on change."""
        self.analysis = kw_or_def('analysis', None)
        """Name of active analysis"""
        self.selected_mj = kw_or_def('selected_mj', None)
        """Selected multijob in UI"""
        self.local_env = kw_or_def('local_env', None)
        """Selected multijob in UI"""

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        self.notify()

    def notify(self):
        for observer in self.observers:
            observer.notify()

    @staticmethod
    def open():
        directory = os.path.join(BASE_DIR, ConfigData.DIR)
        config = cfg.get_config_file(ConfigData.FILE_NAME, directory, cls=ConfigData)
        if config is None:
            config = ConfigData()
        return config

    def save(self):
        directory = os.path.join(BASE_DIR, ConfigData.DIR)
        cfg.save_config_file(ConfigData.FILE_NAME, self, directory)


class DataContainer:
    """
    Wrapper class for all data containers.
    """

    DEBUG_MODE = False

    def __init__(self):
        self.workspaces = None
        self.multijobs = None
        self.ssh_presets = None
        self.pbs_presets = None
        self.resource_presets = None
        self.env_presets = None
        self.config = None
        self.open_all()
        self.pause_func = None
        self.reload_func = None
        
    def set_reload_funcs(self, pause_func, reload_func):
        """
        Set functions for pausing and resuming all processes. 
        This functions is use for resetting 
        """
        self.pause_func = pause_func
        self.reload_func = reload_func

    def save_all(self):
        """
        Saves all data containers for app.
        :return:
        """
        self.workspaces.save(self.config.selected_mj, self.config.analysis)
        self.multijobs.save(self.workspaces.get_id())
        self.ssh_presets.save()
        self.pbs_presets.save()
        self.resource_presets.save()
        self.env_presets.save()
        self.config.save()
        
    def save_mj(self, mj=None):
        """
        Saves only mj data for app.
        :return:
        """
        self.multijobs.save(self.workspaces.get_id())
        self.backup_presets()

    def open_all(self):
        """
        Loads all data containers for app.
        :return:
        """
        self.workspaces = WorkspacesConf.open()
        self.multijobs = MultiJobData.open( self.workspaces.get_id(), self.workspaces.get_path())
        self.ssh_presets = SshData.open()
        self.pbs_presets = PbsData.open()
        self.resource_presets = ResourcesData.open()
        self.env_presets = EnvPresets.open()
        self.config = ConfigData.open()
        
    def backup_presets(self):
        """backup actual presets to workspace dir"""
        self.workspaces. save_to_workspace(
            {
                'IESsh':self.ssh_presets,
                'IEPbs':self.pbs_presets, 
                'IERes':self.resource_presets, 
                'IEEnv':self.env_presets, 
                'IEMj':self.multijobs
            }
            )
    
    def reload_workspace(self, path):
        """
        Reload selected worspace
        
        Call this function after succesful selection of workspace
        and pausing workspace jobs
        """
        if self.workspaces.select_workspace(path, self):
            if not Analysis.exists(self.workspaces.get_path(), self.config.analysis):
                self.config.analysis = None
            self.pause_func()
            self.multijobs = MultiJobData.open(self.workspaces.get_id(), self.workspaces.get_path())            
            self.reload_func()            
            self.config.selected_mj = self.workspaces.get_selected_mj()
            self.config.analysis = self.workspaces.get_selected_analysis() 
            self.save_mj()
            self.config.save()
            
          
            return True
        return False
