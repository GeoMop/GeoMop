# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
import uuid

import config as cfg


class ID(object):
    @staticmethod
    def id():
        """
        Generate ID so that all data structures have same implementation.
        """
        generated_id = str(uuid.uuid4())
        logging.info('ID %s generated.', generated_id)
        return generated_id


class PersistentDict(dict):
    DIR = "mydictfolder"
    NAME = "mydictname"

    def save(self):
        cfg.save_config_file(self.NAME, dict(self.items()), self.DIR)
        logging.info('%s saved successfully.', self.__class__.__name__)

    def load(self, clear=True):
        tmp = cfg.get_config_file(self.NAME, self.DIR)
        if clear:
            self.clear()
        if tmp:
            self.update(tmp.items())
        logging.info('%s loaded successfully.', self.__class__.__name__)


class MultiJobData(PersistentDict):
    DIR = "mj"
    NAME = "mj"


class SshData(PersistentDict):
    DIR = "ssh"
    NAME = "ssh"


class PbsData(PersistentDict):
    DIR = "pbs"
    NAME = "pbs"


class ResourcesData(PersistentDict):
    DIR = "resources"
    NAME = "resources"


class DataContainer(object):
    multijobs = MultiJobData()
    ssh_presets = SshData()
    pbs_presets = PbsData()
    resources_presets = ResourcesData()

    def __init__(self):
        self.load_all()
        self.fill_mock_data()

    def save_all(self):
        self.multijobs.save()
        self.ssh_presets.save()
        self.pbs_presets.save()
        self.resources_presets.save()
        logging.info('==== Everything saved successfully! ====')

    def load_all(self):
        self.multijobs.load()
        if not self.multijobs:
            self.multijobs = MultiJobData()

        self.ssh_presets.load()
        if not self.ssh_presets:
            self.ssh_presets = SshData()

        self.pbs_presets.load()
        if not self.pbs_presets:
            self.pbs_presets = PbsData()

        self.resources_presets.load()
        if not self.resources_presets:
            self.resources_presets = ResourcesData()
        logging.info('==== Everything loaded successfully! ====')

    def fill_mock_data(self):
        self.resources_presets["klic"] = ["Jmeno", "Data"]
        self.resources_presets["klic1"] = ["Jmeno1", "Data"]
        self.resources_presets["klic2"] = ["Zuzan", "Data"]
        self.resources_presets["klic3"] = ["Altos", "Data"]
