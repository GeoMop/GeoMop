# -*- coding: utf-8 -*-
"""
Factory for generating config files.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import logging
import uuid
import data.communicator_conf as comconf
from communication import installation as inst
from data.communicator_conf import PbsConfig, SshConfig, PythonEnvConfig, \
    LibsEnvConfig, CommunicatorConfig, CommType, OutputCommType, InputCommType
from ui.dialogs.resource_dialog import UiResourceDialog

logger = logging.getLogger("UiTrace")


class ConfigBuilder:
    def __init__(self, data):
        self.multijobs = data.multijobs
        self.ssh_presets = data.ssh_presets
        self.pbs_presets = data.pbs_presets
        self.resource_presets = data.resource_presets
        self.env_presets = data.env_presets

    def build(self, key):
        """
        Build json config files into the ./jobs/mj_name/mj_conf
        """
        # multijob properties
        mj_preset = self.multijobs[key].preset
        mj_name = mj_preset.name
        mj_log_level = mj_preset.log_level
        mj_number_of_processes = mj_preset.number_of_processes

        res_preset = self.resource_presets[mj_preset.resource_preset]
        mj_env_preset = self.env_presets[res_preset.mj_env]
        j_env_preset = self.env_presets[res_preset.j_env]

        conf_factory = ConfigFactory()

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
            ConfigFactory.get_env_configs(mj_env_preset)
        # make app_config path and create folder
        conf_dir = inst.Installation.get_config_dir_static(mj_name)
        app_conf_path = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.app.value)
        if res_preset.mj_execution_type == UiResourceDialog.DELEGATOR_LABEL:
            app_conf.next_communicator = comconf.CommType.delegator.value
            app_conf.output_type = comconf.OutputCommType.ssh
            app_conf.ssh = ConfigFactory.get_ssh_config(
                preset=self.ssh_presets[res_preset.mj_ssh_preset])
            # delegator config PBS or EXEC
            delegator_conf = conf_factory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comconf.CommType.delegator)
            delegator_conf.python_env, delegator_conf.libs_env = \
                ConfigFactory.get_env_configs(mj_env_preset)
            # make app_config path and create folder
            delegator_conf_path = comconf.CommunicatorConfigService \
                .get_file_path(conf_dir, comconf.CommType.delegator.value)
            if res_preset.mj_pbs_preset == UiResourceDialog.PBS_LABEL:
                delegator_conf.output_type = comconf.OutputCommType.pbs
                delegator_conf.pbs = ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[res_preset[
                        res_preset.mj_pbs_preset]])

        # mj configs
        mj_conf = conf_factory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.multijob)
        mj_conf.python_env, mj_conf.libs_env = \
            ConfigFactory.get_env_configs(j_env_preset, True)
        # make app_config path and create folder
        mj_path_string = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.multijob.value)
        if res_preset.mj_remote_execution_type == UiResourceDialog.PBS_LABEL:
            mj_conf.input_type = comconf.InputCommType.pbs
        if res_preset.j_execution_type == UiResourceDialog.REMOTE_LABEL:
            mj_conf.next_communicator = comconf.CommType.remote.value
            mj_conf.output_type = comconf.OutputCommType.ssh
            mj_conf.libs_env.install_job_libs = False
            mj_conf.ssh = ConfigFactory.get_ssh_config(
                preset=self.ssh_presets[res_preset.j_ssh_preset])
        elif res_preset.j_execution_type == UiResourceDialog.PBS_LABEL:
            mj_conf.next_communicator = comconf.CommType.job.value
            mj_conf.output_type = comconf.OutputCommType.pbs
            mj_conf.pbs = ConfigFactory.get_pbs_config(
                preset=self.pbs_presets[res_preset.j_pbs_preset])

        # after mj configs EXEC or REMOTE or PBS
        remote_conf = None
        remote_conf_path = None
        job_conf = conf_factory.get_communicator_config(
            communicator=basic_conf,
            preset_type=comconf.CommType.job)
        job_conf.python_env, job_conf.libs_env = \
            ConfigFactory.get_env_configs(j_env_preset, False, True)
        # make job_config path and create folder
        job_conf_path = comconf.CommunicatorConfigService.get_file_path(
            conf_dir, comconf.CommType.job.value)
        if res_preset.j_execution_type == UiResourceDialog.REMOTE_LABEL:
            remote_conf = conf_factory.get_communicator_config(
                communicator=basic_conf,
                preset_type=comconf.CommType.remote)
            remote_conf.python_env, remote_conf.libs_env = \
                ConfigFactory.get_env_configs(j_env_preset, True)
            # make remote_config path and create folder
            remote_conf_path = comconf.CommunicatorConfigService.get_file_path(
                conf_dir, comconf.CommType.remote.value)
            if res_preset.j_remote_execution_type == \
                    UiResourceDialog.PBS_LABEL:
                remote_conf.output_type = comconf.OutputCommType.pbs
                remote_conf.pbs = ConfigFactory.get_pbs_config(
                    preset=self.pbs_presets[res_preset.j_pbs_preset])
                job_conf.input_type = comconf.InputCommType.pbs
            elif res_preset.j_remote_execution_type == \
                    UiResourceDialog.EXEC_LABEL:
                job_conf.input_type = comconf.InputCommType.std
        elif res_preset.j_execution_type == UiResourceDialog.PBS_LABEL:
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


class ConfigFactory(object):
    def __init__(self):
        """init"""
        from version import Version
        version = Version()
        self.app_version = version.version
        """
        Applicationj version. If version in remote installation is different
        new instalation is created
        """

        self.conf_long_id = str(uuid.uuid4())
        """
        Long id of configuration. If  in remote installation is different
        id new configuration is reloaded
        """

    @staticmethod
    def get_pbs_config(preset=None, with_socket=True):
        """
        Converts dialog data into PbsConfig instance
        """
        pbs = PbsConfig()
        if preset:
            pbs.name = preset.name
            # preset[0] is useless description
            pbs.walltime = preset.walltime
            pbs.nodes = preset.nodes
            pbs.ppn = preset.ppn
            pbs.mem = preset.mem
            pbs.scratch = preset.scratch
        else:
            pbs.name = None
            pbs.walltime = ""
            pbs.nodes = "1"
            pbs.ppn = "1"
            pbs.mem = "400mb"
            pbs.scratch = "400mb"
        if with_socket:
            pbs.with_socket = with_socket
        return pbs

    @staticmethod
    def get_ssh_config(preset=None):
        """
        Converts dialog data into SshConfig instance
        """
        ssh = SshConfig()
        if preset:
            ssh.name = preset.name
            # preset[0] is useless description
            ssh.host = preset.host
            ssh.port = preset.port
            ssh.uid = preset.uid
            ssh.pwd = preset.pwd
        return ssh

    @staticmethod
    def get_env_configs(preset=None, install_job_libs=False,
                        start_job_libs=False):
        """
        Converts dialog data into EnvConfigs instance
        """
        python_env = PythonEnvConfig()
        libs_env = LibsEnvConfig()
        if preset.python_exec:
            python_env.python_exec = preset.python_exec
        if preset.scl_enable_exec:
            python_env.scl_enable_exec = preset.scl_enable_exec
        if preset.module_add:
            python_env.module_add = preset.module_add
        if preset.mpi_scl_enable_exec:
            libs_env.mpi_scl_enable_exec = preset.mpi_scl_enable_exec
        if preset.mpi_module_add:
            libs_env.mpi_module_add = preset.mpi_module_add
        if preset.libs_mpicc:
            libs_env.libs_mpicc = preset.libs_mpicc
        libs_env.install_job_libs = install_job_libs
        libs_env.start_job_libs = start_job_libs
        return python_env, libs_env

    def get_communicator_config(self, communicator=None, mj_name=None,
                                log_level=None,
                                preset_type=None):
        """
        Provides preset config for most common communicator types, if you
        provide communicator instance on input with valid preset_type,
        new communicator is derived from original.
        """
        if communicator is None:
            com = CommunicatorConfig(mj_name)
            com.app_version = self.app_version
            com.conf_long_id = self.conf_long_id
        if communicator is not None:
            com = copy.copy(communicator)
        if mj_name is not None:
            com.mj_name = mj_name
        if log_level is not None:
            com.log_level = log_level
        self.preset_common_type(com, preset_type)
        return com

    @staticmethod
    def preset_common_type(com, preset_type=None):
        # app
        if preset_type is CommType.app:
            com.communicator_name = CommType.app.value
            com.next_communicator = CommType.multijob.value
            com.output_type = OutputCommType.exec_
        # delegator
        elif preset_type is CommType.delegator:
            com.communicator_name = CommType.delegator.value
            com.next_communicator = CommType.multijob.value
            com.input_type = InputCommType.std
            com.output_type = OutputCommType.exec_
        # mj
        elif preset_type is CommType.multijob:
            com.communicator_name = CommType.multijob.value
            com.next_communicator = CommType.job.value
            com.input_type = InputCommType.socket
            com.output_type = OutputCommType.exec_
        # remote
        elif preset_type is CommType.remote:
            com.communicator_name = CommType.remote.value
            com.next_communicator = CommType.job.value
            com.input_type = InputCommType.std
            com.output_type = OutputCommType.exec_
        # job
        elif preset_type is CommType.job:
            com.communicator_name = CommType.job.value
            com.next_communicator = CommType.none.value
            com.input_type = InputCommType.socket
            com.output_type = OutputCommType.none
        return com
