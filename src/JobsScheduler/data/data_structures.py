# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import os

import config as cfg
import data.communicator_conf as comcfg
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
    FILE_EXTENSION = ".json"

    multijobs = MultiJobData()
    ssh_presets = SshData()
    pbs_presets = PbsData()
    resource_presets = ResourcesData()

    def __init__(self):
        self.load_all()

    def save_all(self):
        """
        Saves all data containers for app.
        """
        self.multijobs.save()
        self.ssh_presets.save()
        self.pbs_presets.save()
        self.resource_presets.save()
        logging.info('==== Everything saved successfully! ====')

    def load_all(self):
        """
        Loads all data containers for app.
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
        logging.info('==== Everything loaded successfully! ====')

    def build_config_files(self, key, path=DUMP_PATH):
        """
        Build json config files into the ./jobs/mj_name/mj_conf
        """
        # multijob properties
        mj_preset_config = self.multijobs[key]
        mj_name = mj_preset_config[0]
        mj_folder = mj_preset_config[1]
        resource_preset = self.resource_presets[mj_preset_config[3]]
        mj_log_level = mj_preset_config[4]
        mj_number_of_processes = mj_preset_config[5]

        # setup basic conf
        basic_conf = comcfg.ConfigFactory.get_communicator_config(
            mj_name=mj_name, log_level=mj_log_level)

        # setup base path
        base_path = list(path)
        base_path.append(mj_name)
        base_path.append(self.CONFIG_FOLDER)
        os.makedirs(os.path.dirname(os.path.join(*base_path)), exist_ok=True)

        # before mj configs SSH or EXEC
        app_conf = comcfg.ConfigFactory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comcfg.CommType.app)
        delegator_conf = None
        delegator_path_string = None
        # make app_config path and create folder
        app_path = list(base_path)
        app_path.append(app_conf.communicator_name + self.FILE_EXTENSION)
        app_path_string = os.path.join(*app_path)
        if resource_preset[2] == UiResourceDialog.DELEGATOR_LABEL:
            app_conf.next_communicator = comcfg.CommType.delegator.value
            app_conf.output_type = comcfg.OutputCommType.ssh
            app_conf.ssh = comcfg.ConfigFactory.get_ssh_config(
                preset=self.ssh_presets[resource_preset[3]])
            # delegator config PBS or EXEC
            delegator_conf = comcfg.ConfigFactory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comcfg.CommType.delegator)
            # make app_config path and create folder
            delegator_path = list(base_path)
            delegator_path.append(delegator_conf.communicator_name +
                                  self.FILE_EXTENSION)
            delegator_path_string = os.path.join(*delegator_path)
            if resource_preset[4] == UiResourceDialog.PBS_LABEL:
                delegator_conf.output_type = comcfg.OutputCommType.pbs
                delegator_conf.pbs = comcfg.ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[resource_preset[5]],
                    with_socket=True)

        # mj configs
        mj_conf = comcfg.ConfigFactory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comcfg.CommType.multijob)
        # make app_config path and create folder
        mj_path = list(base_path)
        mj_path.append(mj_conf.communicator_name + self.FILE_EXTENSION)
        mj_path_string = os.path.join(*mj_path)
        if resource_preset[4] == UiResourceDialog.PBS_LABEL:
            mj_conf.input_type = comcfg.InputCommType.pbs
        if resource_preset[6] == UiResourceDialog.REMOTE_LABEL:
            mj_conf.next_communicator = comcfg.CommType.remote.value
            mj_conf.output_type = comcfg.OutputCommType.ssh
            mj_conf.ssh = comcfg.ConfigFactory.get_ssh_config(
                preset=self.ssh_presets[resource_preset[7]])
        elif resource_preset[6] == UiResourceDialog.PBS_LABEL:
            mj_conf.next_communicator = comcfg.CommType.remote.value
            mj_conf.output_type = comcfg.OutputCommType.pbs
            mj_conf.pbs = comcfg.ConfigFactory.get_pbs_config(
                preset=self.pbs_presets[resource_preset[9]])

        # after mj configs EXEC or REMOTE or PBS
        remote_conf = None
        remote_path_string = None
        job_conf = comcfg.ConfigFactory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comcfg.CommType.job)
        # make job_config path and create folder
        job_path = list(base_path)
        job_path.append(job_conf.communicator_name + self.FILE_EXTENSION)
        job_path_string = os.path.join(*job_path)
        if resource_preset[6] == UiResourceDialog.REMOTE_LABEL:
            remote_conf = comcfg.ConfigFactory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comcfg.CommType.remote)
            # make remote_config path and create folder
            remote_path = list(base_path)
            remote_path.append(remote_conf.communicator_name +
                               self.FILE_EXTENSION)
            remote_path_string = os.path.join(*remote_path)
            if resource_preset[8] == UiResourceDialog.PBS_LABEL:
                remote_conf.output_type = comcfg.OutputCommType.pbs
                remote_conf.pbs = comcfg.ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[resource_preset[9]])
                job_conf.input_type = comcfg.InputCommType.pbs
            elif resource_preset[8] == UiResourceDialog.EXEC_LABEL:
                job_conf.input_type = comcfg.InputCommType.std
        elif resource_preset[6] == UiResourceDialog.PBS_LABEL:
            job_conf.input_type = comcfg.InputCommType.pbs

        # save to files
        with open(app_path_string, "w") as app_file:
            app_conf.save_to_json_file(app_file)
        if delegator_conf:
            with open(delegator_path_string, "w") as delegator_file:
                delegator_conf.save_to_json_file(delegator_file)
        with open(mj_path_string, "w") as mj_file:
            mj_conf.save_to_json_file(mj_file)
        if remote_conf:
            with open(remote_path_string, "w") as remote_file:
                remote_conf.save_to_json_file(remote_file)
        with open(job_path_string, "w") as job_file:
            job_conf.save_to_json_file(job_file)
        logging.info('==== All configs dumped to JSON in %s! ====',
                     os.path.join(*base_path))

        # return app_config, it is always entry point for next operations
        return app_conf

    def load_from_config_files(self, path):
        """
        Loads json files.
        """
        pass
