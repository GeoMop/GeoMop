# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os

import config as cfg
from geomop_util import Serializable

from .preset_data import EnvPreset, PbsPreset, ResPreset, SshPreset
from .mj_data import MultiJob


BASE_DIR = 'JobScheduler'


class PersistentDict(dict):
    """Persistent dictionary containing configuration."""

    @staticmethod
    def open(cls):
        directory = os.path.join(BASE_DIR, cls.DIR)
        config = cfg.get_config_file(cls.FILE_NAME, directory, cls=cls)
        if config is None:
            config = cls()
        return config

    def save(self):
        directory = os.path.join(BASE_DIR, self.DIR)
        cfg.save_config_file(self.FILE_NAME, self, directory)


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
    def open():
        return PersistentDict.open(MultiJobData)


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
        self.project = kw_or_def('project', None)
        """Name of active project"""
        self.workspace = kw_or_def('workspace', None)
        """Path to selected workspace"""
        self.selected_mj = kw_or_def('selected_mj', None)
        """Selected multijob in UI"""

    def __setattr__(self, key, value):
        self.__dict__[key] = value
        self.notify()

    def notify(self):
        for observer in self.observers:
            observer.notify(self)

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

    BASE_DIR = "JobScheduler"

    def __init__(self):
        self.multijobs = None
        self.ssh_presets = None
        self.pbs_presets = None
        self.resource_presets = None
        self.env_presets = None
        self.config = None
        self.open_all()

    def save_all(self):
        """
        Saves all data containers for app.
        :return:
        """
        self.multijobs.save()
        self.ssh_presets.save()
        self.pbs_presets.save()
        self.resource_presets.save()
        self.env_presets.save()
        self.config.save()

    def open_all(self):
        """
        Loads all data containers for app.
        :return:
        """
        self.multijobs = MultiJobData.open()
        self.ssh_presets = SshData.open()
        self.pbs_presets = PbsData.open()
        self.resource_presets = ResourcesData.open()
        self.env_presets = EnvPresets.open()
        self.config = ConfigData.open()
