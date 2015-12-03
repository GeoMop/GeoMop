# -*- coding: utf-8 -*-
"""
JobScheduler data structures
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import config as cfg
import data.communicator_conf as comconf

from communication import installation as inst
from ui.dialogs.resource_dialog import UiResourceDialog

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


class EnvData(PersistentDict):
    """
    Child class for ENV data.
    """
    DIR = "environments"
    FILE_NAME = "environments"


class DataContainer(object):
    """
    Wrapper class for all data containers.
    """
    multijobs = MultiJobData()
    ssh_presets = SshData()
    pbs_presets = PbsData()
    resource_presets = ResourcesData()
    env_presets = EnvData()

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
            self.env_presets = EnvData()
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
        env_preset1 = self.env_presets[resource_preset[10]]
        env_preset2 = self.env_presets[resource_preset[11]]
        mj_log_level = mj_preset_config[4]
        mj_number_of_processes = mj_preset_config[5]
        
        conf_factory = comconf.ConfigFactory()

        # setup basic conf
        basic_conf = conf_factory.get_communicator_config(
            mj_name=mj_name, log_level=mj_log_level)
        basic_conf.number_of_processes = mj_number_of_processes

        # before mj configs SSH or EXEC
        delegator_conf = None
        delegator_conf_path = None
        app_conf = conf_factory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.app)
        app_conf.python_env, app_conf.libs_env = \
            comconf.ConfigFactory.get_env_configs(env_preset1)
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
            delegator_conf = conf_factory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comconf.CommType.delegator)
            delegator_conf.python_env, delegator_conf.libs_env = \
                comconf.ConfigFactory.get_env_configs(env_preset1)
            # make app_config path and create folder
            delegator_conf_path = comconf.CommunicatorConfigService \
                .get_file_path(conf_dir, comconf.CommType.delegator.value)
            if resource_preset[4] == UiResourceDialog.PBS_LABEL:
                delegator_conf.output_type = comconf.OutputCommType.pbs
                delegator_conf.pbs = comconf.ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[resource_preset[5]])

        # mj configs
        mj_conf = conf_factory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.multijob)
        mj_conf.python_env, mj_conf.libs_env = \
            comconf.ConfigFactory.get_env_configs(env_preset2, True)
        # make app_config path and create folder
        mj_path_string = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.multijob.value)
        if resource_preset[4] == UiResourceDialog.PBS_LABEL:
            mj_conf.input_type = comconf.InputCommType.pbs
        if resource_preset[6] == UiResourceDialog.REMOTE_LABEL:
            mj_conf.next_communicator = comconf.CommType.remote.value
            mj_conf.output_type = comconf.OutputCommType.ssh
            mj_conf.libs_env.install_job_libs = False
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
        job_conf = conf_factory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.job)
        job_conf.python_env, job_conf.libs_env = \
            comconf.ConfigFactory.get_env_configs(env_preset2, False, True)
        # make job_config path and create folder
        job_conf_path = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.job.value)
        if resource_preset[6] == UiResourceDialog.REMOTE_LABEL:
            remote_conf = conf_factory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comconf.CommType.remote)
            remote_conf.python_env, remote_conf.libs_env = \
                comconf.ConfigFactory.get_env_configs(env_preset2, True)
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

