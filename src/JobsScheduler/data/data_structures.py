# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging

logger = logging.getLogger("UiTrace")

import config as cfg
import data.communicator_conf as comconf
from communication import installation as inst
from ui.dialogs.resource_dialog import UiResourceDialog


class PersistentDict(dict):
    DIR = "mydictfolder"
    NAME = "mydictname"

    def save(self):
        cfg.save_config_file(self.NAME, dict(self.items()), self.DIR)

    def load(self, clear=True):
        tmp = cfg.get_config_file(self.NAME, self.DIR)
        if clear:
            self.clear()
        if tmp:
            self.update(tmp.items())


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
        logger.info('==== Everything saved successfully! ====')

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
        logger.info('==== Everything loaded successfully! ====')

    def build_config_files(self, key):
        """
        Build json config files into the ./jobs/mj_name/mj_conf
        """
        # multijob properties
        mj_preset_config = self.multijobs[key]["preset"]
        mj_name = mj_preset_config[0]
        mj_folder = mj_preset_config[1]
        resource_preset = self.resource_presets[mj_preset_config[3]]
        # env_preset1 = self.resource_presets[mj_preset_config[12]]
        # env_preset2 = self.resource_presets[mj_preset_config[13]]
        mj_log_level = mj_preset_config[4]
        mj_number_of_processes = mj_preset_config[5]

        # setup basic conf
        basic_conf = comconf.ConfigFactory.get_communicator_config(
            mj_name=mj_name, log_level=mj_log_level)
        basic_conf.number_of_processes = mj_number_of_processes

        # before mj configs SSH or EXEC
        app_conf = comconf.ConfigFactory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.app)
        delegator_conf = None
        delegator_conf_path = None
        # make app_config path and create folder
        conf_dir = inst.Installation.get_config_dir_static(mj_name)
        app_conf_path = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.app.value)
        if resource_preset[2] == UiResourceDialog.DELEGATOR_LABEL:
            app_conf.next_communicator = comconf.CommType.delegator.value
            app_conf.output_type = comconf.OutputCommType.ssh
            app_conf.ssh = comconf.ConfigFactory.get_ssh_config(
                preset=self.ssh_presets[resource_preset[3]])
            # delegator config PBS or EXEC
            delegator_conf = comconf.ConfigFactory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comconf.CommType.delegator)
            delegator_conf.python_exec = resource_preset[10]
            # make app_config path and create folder
            delegator_conf_path = comconf.CommunicatorConfigService \
                .get_file_path(conf_dir, comconf.CommType.delegator.value)
            if resource_preset[4] == UiResourceDialog.PBS_LABEL:
                delegator_conf.output_type = comconf.OutputCommType.pbs
                delegator_conf.pbs = comconf.ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[resource_preset[5]],
                    with_socket=True)

        # mj configs
        mj_conf = comconf.ConfigFactory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.multijob)
        mj_conf.python_exec = resource_preset[10]
        # make app_config path and create folder
        mj_path_string = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.multijob.value)
        if resource_preset[4] == UiResourceDialog.PBS_LABEL:
            mj_conf.input_type = comconf.InputCommType.pbs
        if resource_preset[6] == UiResourceDialog.REMOTE_LABEL:
            mj_conf.next_communicator = comconf.CommType.remote.value
            mj_conf.output_type = comconf.OutputCommType.ssh
            mj_conf.ssh = comconf.ConfigFactory.get_ssh_config(
                preset=self.ssh_presets[resource_preset[7]])
        elif resource_preset[6] == UiResourceDialog.PBS_LABEL:
            mj_conf.next_communicator = comconf.CommType.job.value
            mj_conf.output_type = comconf.OutputCommType.pbs
            mj_conf.pbs = comconf.ConfigFactory.get_pbs_config(
                preset=self.pbs_presets[resource_preset[9]])

        # after mj configs EXEC or REMOTE or PBS
        remote_conf = None
        remote_conf_path = None
        job_conf = comconf.ConfigFactory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.job)
        job_conf.python_exec = resource_preset[11]
        # make job_config path and create folder
        job_conf_path = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.job.value)
        if resource_preset[6] == UiResourceDialog.REMOTE_LABEL:
            remote_conf = comconf.ConfigFactory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comconf.CommType.remote)
            delegator_conf.python_exec = resource_preset[11]
            # make remote_config path and create folder
            remote_conf_path = comconf.CommunicatorConfigService.get_file_path(
                conf_dir, comconf.CommType.remote.value)
            if resource_preset[8] == UiResourceDialog.PBS_LABEL:
                remote_conf.output_type = comconf.OutputCommType.pbs
                remote_conf.pbs = comconf.ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[resource_preset[9]])
                job_conf.input_type = comconf.InputCommType.pbs
            elif resource_preset[8] == UiResourceDialog.EXEC_LABEL:
                job_conf.input_type = comconf.InputCommType.std
        elif resource_preset[6] == UiResourceDialog.PBS_LABEL:
            job_conf.input_type = comconf.InputCommType.pbs

        # save to files
        with open(app_conf_path, "w") as app_file:
            comconf.CommunicatorConfigService.save_file(
                app_file, app_conf)
        if delegator_conf:
            with open(delegator_conf_path, "w") as delegator_file:
                comconf.CommunicatorConfigService.save_file(
                    delegator_file, delegator_conf)
        with open(mj_path_string, "w") as mj_file:
            comconf.CommunicatorConfigService.save_file(
                mj_file, mj_conf)
        if remote_conf:
            with open(remote_conf_path, "w") as remote_file:
                comconf.CommunicatorConfigService.save_file(
                    remote_file, remote_conf)
        with open(job_conf_path, "w") as job_file:
            comconf.CommunicatorConfigService.save_file(
                job_file, job_conf)
        logger.info('==== All configs dumped to JSON in %s! ====', conf_dir)

        # return app_config, it is always entry point for next operations
        return app_conf

    def load_from_config_files(self, path):
        """
        Loads json files.
        """
        pass
