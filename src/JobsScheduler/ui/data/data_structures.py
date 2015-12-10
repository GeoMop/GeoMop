# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import config as cfg

logger = logging.getLogger("UiTrace")


class PersistentDict(dict):
    """
    Parent class for persistent data derived from dict.
    DIR and FILE_NAME should be overridden in child for custom folder and
    filename.
    """
    DIR = "mydictfolder"
    FILE_NAME = "mydictname"

    def save(self):
        """
        Method for saving data to custom DIR/FILE_NAME.
        :return:
        """
        cfg.save_config_file(self.FILE_NAME, dict(self.items()), self.DIR)

    def load(self, clear=True):
        """
        Loads from custom DIR/FILE_NAME.
        :return:
        """
        tmp = cfg.get_config_file(self.FILE_NAME, self.DIR)
        if clear:
            self.clear()
        if tmp:
            self.update(tmp.items())


class MultiJobData(PersistentDict):
    """
    Child class for MJ data.
    """
    DIR = "mj"
    FILE_NAME = "mj"


class SshData(PersistentDict):
    """
    Child class for SSH data.
    """
    DIR = "ssh"
    FILE_NAME = "ssh"


class PbsData(PersistentDict):
    """
    Child class for PBS data.
    """
    DIR = "pbs"
    FILE_NAME = "pbs"


class ResourcesData(PersistentDict):
    """
    Child class for RES data.
    """
    DIR = "resources"
    FILE_NAME = "resources"


class EnvPresets(PersistentDict):
    """
    Child class for ENV data.
    """
    DIR = "environments"
    FILE_NAME = "environments"


class SetData(PersistentDict):
    """
    Child class for SET data.
    """
    DIR = "settings"
    FILE_NAME = "settings"


class DataContainer(object):
    """
    Wrapper class for all data containers.
    """
    multijobs = MultiJobData()
    ssh_presets = SshData()
    pbs_presets = PbsData()
    resource_presets = ResourcesData()
    env_presets = EnvPresets()
    set_data = SetData()

    def __init__(self):
        self.load_all()

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
        self.set_data.save()
        logger.info('==== Everything saved successfully! ====')

    def load_all(self):
        """
        Loads all data containers for app.
        :return:
        """
        self.multijobs.load()
        if not self.multijobs:
            self.multijobs = MultiJobData()

        self.ssh_presets.load()
        if not self.ssh_presets:
            self.ssh_presets = SshData()

        self.pbs_presets.load()
        if not self.pbs_presets:
            self.pbs_presets = PbsData()

        self.resource_presets.load()
        if not self.resource_presets:
            self.resource_presets = ResourcesData()

        self.env_presets.load()
        if not self.env_presets:
            self.env_presets = EnvPresets()

        self.set_data.load()
        if not self.set_data:
            self.set_data = SetData()
        logger.info('==== Everything loaded successfully! ====')
