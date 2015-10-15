# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
import os
import uuid

import config as cfg
import data.my_communicator_conf as comcfg


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
    DUMP_PATH = (".", "jobs")
    CONFIG_FOLDER = ("mj_conf")

    multijobs = MultiJobData()
    ssh_presets = SshData()
    pbs_presets = PbsData()
    resource_presets = ResourcesData()

    def __init__(self):
        self.load_all()

    def save_all(self):
        self.multijobs.save()
        self.ssh_presets.save()
        self.pbs_presets.save()
        self.resource_presets.save()
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

        self.resource_presets.load()
        if not self.resource_presets:
            self.resource_presets = ResourcesData()
        logging.info('==== Everything loaded successfully! ====')

    def build_config_files(self, key, path=DUMP_PATH):
        mj = self.multijobs[key]

        base_path = list(path)
        base_path.append(mj[0])
        base_path.append(self.CONFIG_FOLDER)

        app_conf = comcfg.CommunicatorConfig()
        app_conf.output_type = comcfg.OutputCommType.ssh
        app_conf.communicator_name = "app"
        app_conf.mj_name = "m5j"
        app_conf.next_communicator = "delegator"
        app_conf.ssh.uid = "test"
        app_conf.ssh.pwd = "MojeHeslo123"
        app_conf.ssh.host = "localhost"
        app_conf.pbs = comcfg.PbsConfig()
        app_conf.log_level = logging.DEBUG

        app_path = list(base_path)
        app_path.append(app_conf.communicator_name + ".json")
        app_path_string = os.path.join(*app_path)
        os.makedirs(os.path.dirname(app_path_string), exist_ok=True)
        with open(app_path_string, "w") as app_file:
            app_conf.save_to_json_file(app_file)
            conf = comcfg.CommunicatorConfig()
        with open(app_path_string, "r") as app_file:
            conf.load_from_json_file(app_file)

    def load_from_config_files(self, path):
        pass
