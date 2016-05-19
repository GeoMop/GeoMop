# -*- coding: utf-8 -*-
"""
Factory for generating config files.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import os
import uuid
import json

from communication import Installation
from communication.installation import __ins_files__
from data.communicator_conf import PbsConfig, SshConfig, PythonEnvConfig, \
    LibsEnvConfig, CommunicatorConfig, CommType, OutputCommType, InputCommType, \
    CommunicatorConfigService
from ui.dialogs.resource_dialog import UiResourceDialog
from version import Version

JOB_NAME_LABEL = "flow"


class ConfigBuilder:
    def __init__(self, data):
        self.multijobs = data.multijobs
        self.ssh_presets = data.ssh_presets
        self.pbs_presets = data.pbs_presets
        self.resource_presets = data.resource_presets
        self.env_presets = data.env_presets

        self.app_version = Version().version
        """
        Application version. If version in remote installation is different
        new installation is created.
        """

        self.conf_long_id = str(uuid.uuid4())
        """
        Long id of configuration. If  in remote installation is different
        id new configuration is reloaded.
        """

    def build(self, key):
        """
        Build json config files into the ./jobs/mj_name/mj_conf
        :param key: Identification of preset.
        :return: app_conf
        """
        # multijob preset properties
        mj_preset = self.multijobs[key].preset
        mj_name = mj_preset.name
        res_preset = self.resource_presets[mj_preset.resource_preset]
        mj_log_level = mj_preset.log_level
        mj_number_of_processes = mj_preset.number_of_processes

        # resource preset
        mj_execution_type = res_preset.mj_execution_type
        mj_ssh_preset = self.ssh_presets.get(res_preset.mj_ssh_preset, None)
        mj_remote_execution_type = res_preset.mj_remote_execution_type
        mj_pbs_preset = self.pbs_presets.get(res_preset.mj_pbs_preset, None)
        mj_env = self.env_presets[res_preset.mj_env]

        j_execution_type = res_preset.j_execution_type
        j_ssh_preset = self.ssh_presets.get(res_preset.j_ssh_preset, None)
        j_remote_execution_type = res_preset.j_remote_execution_type
        j_pbs_preset = self.pbs_presets.get(res_preset.j_pbs_preset, None)
        j_env = self.env_presets[res_preset.j_env]

        # init conf
        basic_conf = CommunicatorConfig()
        basic_conf.mj_name = mj_name
        basic_conf.log_level = mj_log_level
        basic_conf.number_of_processes = mj_number_of_processes
        basic_conf.app_version = self.app_version
        basic_conf.conf_long_id = self.conf_long_id

        # make conf
        mj_ssh = ConfFactory.get_ssh_conf(mj_ssh_preset)
        mj_dialect = mj_ssh_preset.pbs_system if hasattr(mj_ssh_preset, "pbs_system") else None
        mj_pbs = ConfFactory.get_pbs_conf(mj_pbs_preset, True, pbs_params=mj_env.pbs_params,
                                          dialect=mj_dialect)
        mj_python_env, mj_libs_env = ConfFactory.get_env_conf(mj_env)

        # env conf
        j_ssh = ConfFactory.get_ssh_conf(j_ssh_preset)
        j_dialect = j_ssh_preset.pbs_system if hasattr(j_ssh_preset, "pbs_system") else None
        if (res_preset.mj_execution_type == UiResourceDialog.EXEC_LABEL and
                res_preset.j_execution_type == UiResourceDialog.PBS_LABEL) or \
                (res_preset.mj_execution_type == UiResourceDialog.PBS_LABEL and
                res_preset.j_execution_type == UiResourceDialog.PBS_LABEL):
            j_dialect = mj_dialect
        j_pbs = ConfFactory.get_pbs_conf(j_pbs_preset, pbs_params=j_env.pbs_params,
                                         dialect=j_dialect)
        jmj_python_env, jmj_libs_env = ConfFactory.get_env_conf(j_env)
        # TODO vyresit instalaci a spousteni knihovny
        r_python_env, r_libs_env = ConfFactory.get_env_conf(j_env, False, False)
        j_python_env, j_libs_env = ConfFactory.get_env_conf(j_env, False, False)

        # declare builders
        app = ConfBuilder(basic_conf)
        app.set_comm_name(CommType.app)\
            .set_python_env(mj_python_env)\
            .set_libs_env(mj_libs_env)
        app.conf.central_log = True

        delegator = None

        mj = ConfBuilder(basic_conf)
        mj.set_comm_name(CommType.multijob)\
            .set_python_env(r_python_env)\
            .set_libs_env(r_libs_env)
        # TODO r_python_env, r_libs_env are derived from j_env instead of mj_env - why?
        mj.set_env_extras(mj_env)

        remote = None

        job = ConfBuilder(basic_conf)
        job.set_comm_name(CommType.job)\
            .set_python_env(j_python_env)\
            .set_libs_env(j_libs_env)
        job.set_env_extras(j_env)

        # set data with builders
        if mj_execution_type == UiResourceDialog.EXEC_LABEL:
            app.set_next_comm(CommType.multijob)\
                .set_out_comm(OutputCommType.exec_)
            mj.set_in_comm(InputCommType.socket)

        elif mj_execution_type == UiResourceDialog.DELEGATOR_LABEL:
            app.set_next_comm(CommType.delegator)\
                .set_out_comm(OutputCommType.ssh)\
                .set_ssh(mj_ssh)

            delegator = ConfBuilder(basic_conf)
            delegator.set_comm_name(CommType.delegator)\
                .set_next_comm(CommType.multijob)\
                .set_in_comm(InputCommType.std)\
                .set_python_env(mj_python_env)\
                .set_libs_env(mj_libs_env)
            delegator.set_env_extras(mj_env)
            if mj_remote_execution_type == UiResourceDialog.EXEC_LABEL:
                delegator.set_out_comm(OutputCommType.exec_)
                mj.set_in_comm(InputCommType.socket)
            elif mj_remote_execution_type == UiResourceDialog.PBS_LABEL:
                delegator.set_out_comm(OutputCommType.pbs)\
                    .set_pbs(mj_pbs)
                mj.set_in_comm(InputCommType.pbs)

        if j_execution_type == UiResourceDialog.EXEC_LABEL:
            mj.set_next_comm(CommType.job)\
                .set_out_comm(OutputCommType.exec_)
            job.set_in_comm(InputCommType.socket)
        elif j_execution_type == UiResourceDialog.REMOTE_LABEL:
            mj.set_next_comm(CommType.remote)\
                .set_out_comm(OutputCommType.ssh)\
                .set_ssh(j_ssh)\
                .set_python_env(jmj_python_env)\
                .set_libs_env(jmj_libs_env)
            remote = ConfBuilder(basic_conf)
            remote.set_comm_name(CommType.remote)\
                .set_next_comm(CommType.job)\
                .set_in_comm(InputCommType.std)\
                .set_python_env(r_python_env)\
                .set_libs_env(r_libs_env)
            remote.set_env_extras(j_env)
            if j_remote_execution_type == UiResourceDialog.EXEC_LABEL:
                remote.set_out_comm(OutputCommType.exec_)
                job.set_in_comm(InputCommType.socket)
            elif j_remote_execution_type == UiResourceDialog.PBS_LABEL:
                remote.set_out_comm(OutputCommType.pbs)\
                    .set_pbs(j_pbs)
                job.set_in_comm(InputCommType.pbs)
        elif j_execution_type == UiResourceDialog.PBS_LABEL:
            mj.set_next_comm(CommType.job)\
                .set_out_comm(OutputCommType.pbs)\
                .set_pbs(j_pbs)
            job.set_in_comm(InputCommType.pbs)

        if mj_remote_execution_type == UiResourceDialog.PBS_LABEL and \
           j_execution_type == UiResourceDialog.REMOTE_LABEL and \
           j_remote_execution_type == UiResourceDialog.PBS_LABEL:
            mj.conf.direct_communication = True
            remote.conf.direct_communication = True

        # save to files
        with open(app.get_path(), "w") as app_file:
            CommunicatorConfigService.save_file(
                app_file, app.get_conf())
        if delegator:
            with open(delegator.get_path(), "w") as delegator_file:
                CommunicatorConfigService.save_file(
                    delegator_file, delegator.get_conf())
        with open(mj.get_path(), "w") as mj_file:
            CommunicatorConfigService.save_file(
                mj_file, mj.get_conf())
        if remote:
            with open(remote.get_path(), "w") as remote_file:
                CommunicatorConfigService.save_file(
                    remote_file, remote.get_conf())
        with open(job.get_path(), "w") as job_file:
            CommunicatorConfigService.save_file(
                job_file, job.get_conf())

        # build job configuration
        self._build_jobs_config(mj_name)

        # return app_config, it is always entry point for next operations
        return app.get_conf()

    def _build_jobs_config(self, mj_name):
        """Create jobs and associate them with individual configuration files."""
        jobs = {}
        mj_dir = os.path.join(Installation.get_mj_data_dir_static(mj_name))
        job_configs_path = os.path.join(Installation.get_config_dir_static(mj_name),
                                       __ins_files__['job_configurations'])
        job_counter = 1

        def create_job(configuration_file):
            """Generate job name and create its configuration."""
            nonlocal job_counter
            name = JOB_NAME_LABEL + str(job_counter)
            data = {'configuration_file': configuration_file}
            jobs[name] = data
            job_counter += 1

        # recursively find all configuration files (ending with .yaml)
        for root, directories, filenames in os.walk(mj_dir):
            for filename in filenames:
                if filename.endswith('.yaml'):
                    abs_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(abs_path, start=mj_dir)
                    # windows path workaround
                    rel_path_unix = '/'.join(rel_path.split(os.path.sep))
                    create_job(rel_path_unix)

        # save job configurations to json
        with open(job_configs_path, 'w') as job_configs:
            json.dump(jobs, job_configs, indent=4, sort_keys=True)


class ConfBuilder:
    def __init__(self, basic_conf):
        self.conf = copy.deepcopy(basic_conf)

    def set_comm_name(self, comm_name):
        self.conf.communicator_name = comm_name.value
        return self

    def set_next_comm(self, next_comm):
        self.conf.next_communicator = next_comm.value
        return self

    def set_in_comm(self, in_comm):
        self.conf.input_type = in_comm
        return self

    def set_out_comm(self, out_comm):
        self.conf.output_type = out_comm
        return self

    def set_ssh(self, ssh_conf):
        self.conf.ssh = ssh_conf
        return self

    def set_pbs(self, pbs_conf):
        self.conf.pbs = pbs_conf
        return self

    def set_python_env(self, python_env):
        self.conf.python_env = python_env
        return self

    def set_libs_env(self, libs_env):
        self.conf.libs_env = libs_env
        return self

    def set_env_extras(self, env):
        if self.conf.pbs:
            self.conf.pbs.pbs_params = env.pbs_params
        self.conf.flow_path = env.flow_path
        self.conf.cli_params = env.cli_params

    def get_conf(self):
        """
        Gets internal conf state.
        :return: CommunicatorConf object
        """
        return self.conf

    def get_path(self):
        """
        Get path to conf file.
        :return: Conf file path string.
        """
        path = Installation.get_config_dir_static(self.conf.mj_name)
        file = self.conf.communicator_name + ".json"
        return os.path.join(path, file)


class ConfFactory:
    @staticmethod
    def get_pbs_conf(preset, with_socket=True, pbs_params=None, dialect=None):
        """
        Converts preset data to communicator config for PBS.
        :param preset: Preset data object from UI.
        :param with_socket: Defines if pbs communicates with socket, True in
        case of multijob, otherwise False.
        :return: PbsConf object
        """
        if not preset:
            return None
        pbs = PbsConfig()
        pbs.name = preset.name
        pbs.dialect = dialect
        pbs.queue = preset.queue
        pbs.walltime = preset.walltime
        pbs.nodes = str(preset.nodes)
        pbs.ppn = str(preset.ppn)
        pbs.memory = preset.memory
        pbs.infiniband = preset.infiniband
        pbs.with_socket = with_socket
        if pbs_params is not None:
            pbs.pbs_params = pbs_params
        return pbs

    @staticmethod
    def get_ssh_conf(preset):
        """
        Converts preset data to communicator config for SSH.
        :param preset: Preset data object from UI.
        :return: SshConf object
        """
        if not preset:
            return None
        ssh = SshConfig()
        ssh.name = preset.name
        ssh.host = preset.host
        ssh.port = preset.port
        ssh.uid = preset.uid
        ssh.pwd = preset.pwd
        return ssh

    @staticmethod
    def get_env_conf(preset, install_job_libs=False, start_job_libs=False):
        """
        Converts preset data to communicator config for PythonEnv and LibsEnv.
        :param preset: Preset data object from UI.
        :param install_job_libs: True in case MultiJob or False in MultiJob
        and True in Remote if Remote exist.
        :param start_job_libs: True in case of Job.
        :return: PythonEnvConf object, LibsEnvConf object
        """
        python_env = PythonEnvConfig()
        python_env.python_exec = preset.python_exec
        python_env.scl_enable_exec = preset.scl_enable_exec
        python_env.module_add = preset.module_add

        libs_env = LibsEnvConfig()
        libs_env.install_job_libs = install_job_libs
        libs_env.start_job_libs = start_job_libs
        return python_env, libs_env
