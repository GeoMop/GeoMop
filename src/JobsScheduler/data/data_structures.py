# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import logging
import os

import config as cfg
import data.my_communicator_conf as comcfg
from ui.dialogs.resource_dialog import UiResourceDialog


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
        # multijob properties
        mj_preset_config = self.multijobs[key]
        mj_name = mj_preset_config[0]
        mj_folder = mj_preset_config[1]
        resource_preset = self.resource_presets[mj_preset_config[3]]
        mj_log_level = mj_preset_config[4]
        mj_number_of_processes = mj_preset_config[5]

        # setup basic conf
        basic_conf = comcfg.CommunicatorConfig()
        basic_conf.mj_name = mj_name
        basic_conf.log_level = mj_log_level

        # setup base path
        base_path = list(path)
        base_path.append(mj_name)
        base_path.append(self.CONFIG_FOLDER)
        os.makedirs(os.path.dirname(os.path.join(*base_path)), exist_ok=True)

        # before mj configs SSH or EXEC
        app_conf = copy.copy(basic_conf)
        app_conf.preset_type(comcfg.CommType.app.value)
        delegator_conf = None
        # make app_config path and create folder
        app_path = list(base_path)
        app_path.append(app_conf.communicator_name + ".json")
        app_path_string = os.path.join(*app_path)
        if resource_preset[2] == UiResourceDialog.DELEGATOR_LABEL:
            app_conf.next_communicator = comcfg.CommType.delegator.value
            app_conf.output_type = comcfg.OutputCommType.ssh
            app_conf.ssh = comcfg.SshConfig(preset=self.ssh_presets[
                resource_preset[3]])
            # delegator config PBS or EXEC
            delegator_conf = copy.copy(basic_conf)
            delegator_conf.preset_type(comcfg.CommType.delegator.value)
            # make app_config path and create folder
            delegator_path = list(base_path)
            delegator_path.append(delegator_conf.communicator_name + ".json")
            delegator_path_string = os.path.join(*delegator_path)
            if resource_preset[4] == UiResourceDialog.PBS_LABEL:
                delegator_conf.output_type = comcfg.OutputCommType.pbs
                delegator_conf.pbs = comcfg.PbsConfig(
                    preset=self.pbs_presets[resource_preset[5]],
                    with_socket=True)

        # mj configs
        print(resource_preset)
        mj_conf = copy.copy(basic_conf)
        mj_conf.preset_type(comcfg.CommType.multijob.value)
        remote_conf = None
        # make app_config path and create folder
        mj_path = list(base_path)
        mj_path.append(app_conf.communicator_name + ".json")
        mj_path_string = os.path.join(*mj_path)
        if resource_preset[4] == UiResourceDialog.PBS_LABEL:
            mj_conf.input_type = comcfg.InputCommType.pbs
        if resource_preset[5] == UiResourceDialog.REMOTE_LABEL:
            mj_conf.next_communicator = comcfg.CommType.remote.value
            mj_conf.output_type = comcfg.OutputCommType.ssh
            mj_conf.ssh = comcfg.SshConfig(preset=self.ssh_presets[
                resource_preset[6]])
        elif resource_preset[5] == UiResourceDialog.PBS_LABEL:
            mj_conf.next_communicator = comcfg.CommType.remote.value
            mj_conf.output_type = comcfg.OutputCommType.pbs
            mj_conf.ssh = comcfg.PbsConfig(preset=self.pbs_presets[
                resource_preset[7]])

        # save to files
        with open(app_path_string, "w") as app_file:
            app_conf.save_to_json_file(app_file)
        if delegator_conf:
            with open(delegator_path_string, "w") as delegator_file:
                delegator_conf.save_to_json_file(delegator_file)
        with open(mj_path_string, "w") as mj_file:
            mj_conf.save_to_json_file(mj_file)
        """
        if remote_conf:
            with open(remote_path_string, "w") as remote_file:
                remote_conf.save_to_json_file(remote_file)
        with open(job_path_string, "w") as job_file:
            job_conf.save_to_json_file(job_file)
        """
        logging.info('==== All configs dumped to JSON in %s! ====',
                     os.path.join(*base_path))

    def load_from_config_files(self, path):
        pass
