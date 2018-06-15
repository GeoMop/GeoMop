# -*- coding: utf-8 -*-
"""
MujtiJob data structure.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import os
import time
import copy

from JobPanel.communication import Installation
from JobPanel.data.states import TaskStatus, JobsState
from ..data.preset_data import APreset
from gm_base.geomop_util import Serializable


class MultiJobState:
    """
    Data for current state of MultiJob
    """

    __serializable__ = Serializable(
        composite={'status': TaskStatus}
    )

    def __init__(self, name, **kwargs):
        """
        Default initialization.
        :param name: MultiJob name
        :return: None
        """
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        self.name = name
        """Name of multijob"""
        self.analysis = kw_or_def('analysis')
        """Name of the analysis"""
        self.insert_time = kw_or_def('insert_time', time.time())
        """When MultiJob was started"""
        self.queued_time = kw_or_def('queued_time')
        """When MultiJob was queued"""
        self.start_time = kw_or_def('start_time')
        """When MultiJob was started"""
        self.run_interval = kw_or_def('run_interval', 0)
        """MultiJob run time from start in second"""
        self.status = kw_or_def('status', TaskStatus.none)
        """MultiJob current status"""
        self.known_jobs = kw_or_def('known_jobs', 0)
        """Count of known jobs (minimal amount of jobs)"""
        self.estimated_jobs = kw_or_def('estimated_jobs', 0)
        """Estimated count of jobs"""
        self.finished_jobs = kw_or_def('finished_jobs', 0)
        """Count of finished jobs"""
        self.running_jobs = kw_or_def('running_jobs', 0)
        """Count of running jobs"""
        self.update_time = kw_or_def('update_time')
        """When MultiJobState  was last updated"""
        
    def copy(self, new_status=None):
        """
        Deep copy state
        :param new_status: Set status if is not None
        :return: new state
        """
        new_state =  copy.deepcopy(self)
        if new_status is not None:            
            new_state.status =new_status
        return new_state

    def update(self, new_state):
        """
        Update new_state with received data
        :param new_state: Communication new_state data
        :return: None
        """
        self.queued_time = new_state.queued_time
        self.start_time = new_state.start_time
        self.run_interval = new_state.run_interval
        self.status = new_state.status
        self.known_jobs = new_state.known_jobs
        self.estimated_jobs = new_state.estimated_jobs
        self.finished_jobs = new_state.finished_jobs
        self.running_jobs = new_state.running_jobs

        self.update_time = time.time()

    def get_status(self):
        """
        Return MultiJob status
        :return: Current TaskStatus
        """
        return self.status

    def set_status(self, new_status):
        """
        Directly changes status of the MultiJob
        :param new_status: TaskStatus o replace current.
        :return: None
        """
        self.status = new_status

    def __repr__(self):
        """
        Representation of object
        :return: String representation of object.
        """
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)


class MultiJobPreset(APreset):
    """
    MultiJob preset data container.
    """

    def __init__(self, **kwargs):
        """
        Default initialization.
        :return: None
        """
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        name = kw_or_def('name', 'Default MultiJob Preset Name')
        super().__init__(name)

        self.resource_preset = kw_or_def('resource_preset')
        """Selected resource preset"""
       # self.pbs_preset = kw_or_def('pbs_preset')
        """AdHoc PBS preset override"""
        self.log_level = kw_or_def('log_level', logging.DEBUG)
        """Logging level"""
        self.number_of_processes = kw_or_def('number_of_processes', 1)
        """Number of processes used by MultiJob"""
        self.analysis = kw_or_def('analysis')
        """Name of the analysis used in this multijob"""
        self.from_mj = kw_or_def('from_mj', None)
        """Name of the source multijob (if reused)."""
        self.deleted_remote = kw_or_def('deleted_remote', False)
        """Name of the source multijob (if reused)."""

    def __repr__(self):
        """
        Representation of object
        :return: String representation of object.
        """
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)


class MultiJob:

    __serializable__ = Serializable(
        composite={'preset': MultiJobPreset,
                   'state': MultiJobState}, 
        excluded=['valid']
    )

    def __init__(self, preset, **kwargs):
        def kw_or_def(key, default=None):
            return kwargs[key] if key in kwargs else default

        self.preset = preset
        """mj preset"""
        self.state = kw_or_def('state', MultiJobState(preset.name))
        """mj state"""
        self.error = kw_or_def('error', "")
        """mj error for error state"""
        self.last_status = kw_or_def('last_status', None)
        """State before deleting"""
        self.valid = True

    @property
    def id(self):
        """Get multijob id = analysis_name"""
        return self.preset.analysis + "_" + self.preset.name

    def get_preset(self):
        """
        Get MultiJob preset.
        :return: MultiJobPreset object
        """
        return self.preset

    def get_state(self):
        """
        Return MultiJob state.
        :return: MultiJobState object
        """
        return self.state

    def get_jobs(self):
        """
        Return list of Jobs that belong to MultiJob.
        :return: List of Jobs
        """
        res_path = Installation.get_result_dir_static(self.preset.name, self.preset.analysis)
        states = JobsState()
        states.load_file(res_path)
        return states.jobs

    def get_logs(self):
        """
        Scans log directory and returns log files.
        :return: List of MultiJobLog objects
        """
        log_path = Installation.get_mj_log_dir_static(self.preset.name, self.preset.analysis)
        logs = []
        # for file in os.listdir(log_path):
        #     if os.path.isfile(os.path.join(log_path, file)):
        #         log = MultiJobLog(log_path, file)
        #         logs.append(log)
        mj_config_path = os.path.join(log_path, "..", "..", "mj_config")

        # MJ log
        file = "mj_service.log"
        if os.path.isfile(os.path.join(mj_config_path, file)):
            log = MultiJobLog(os.path.normpath(mj_config_path), file)
            logs.append(log)

        # Jobs log
        for dir in os.listdir(mj_config_path):
            job_dir = os.path.join(mj_config_path, dir)
            if os.path.isdir(job_dir) and dir.startswith("job_"):
                file = "job_service.log"
                if os.path.isfile(os.path.join(job_dir, file)):
                    log = MultiJobLog(os.path.normpath(job_dir), file)
                    logs.append(log)

        return logs

    def get_results(self):
        """
        Scans res directory and returns results files.
        :return: List of MultiJobRes objects
        """
        res_path = Installation.get_result_dir_static(self.preset.name, self.preset.analysis)
        ress = []
        for file in os.listdir(res_path):
            if os.path.isfile(os.path.join(res_path, file)):
                res = MultiJobLog(res_path, file)
                ress.append(res)
        jobs = self.get_jobs()
        for job in jobs:
            dir = os.path.join(res_path, job.name)
            if os.path.isdir(dir):
                ress.extend(self._get_result_from_dir(dir))
        return ress
        
    def _get_result_from_dir(self, dir, recurs=True):
        """return all files in set directory as result"""
        ress = []
        for file in os.listdir(dir):
            new = os.path.join(dir, file)
            if os.path.isfile(new):
                res = MultiJobLog(dir, file)
                ress.append(res)
            elif recurs and os.path.isdir(new):
                ress.extend(self._get_result_from_dir(new))
        return ress
                

    def get_configs(self):
        """
        Scans res directory and returns config files.
        :return: List of MultiJobConf objects
        """
        conf_path = Installation.get_config_dir_static(self.preset.name, self.preset.analysis)
        confs = []
        for file in os.listdir(conf_path):
            if os.path.isfile(os.path.join(conf_path, file)):
                conf = MultiJobLog(conf_path, file)
                confs.append(conf)
        return confs


class AMultiJobFile:
    """
    Abstract data container.
    """

    def __init__(self, path, file):
        """
        Default initialization.
        :return: None
        """
        self.file_name = file
        """Short name of the file"""
        self.file_path = os.path.join(path, file)
        """Path to file"""

        stat_info = os.stat(self.file_path)

        def sizeof_fmt(num, suffix='B'):
            """
            Represents size Integer as String with appropriate unit.
            :param num: Integer representation
            :param suffix: Default suffix
            :return: String representation of size
            """
            for unit in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z']:
                if abs(num) < 1024.0:
                    return "%3.1f%s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.1f%s%s" % (num, 'Y', suffix)

        self.file_size = sizeof_fmt(stat_info.st_size)
        """File size"""

        self.modification_time = stat_info.st_mtime
        """Time of the latest modification"""

        # for later details extension
        # self._stat_info = stat_info
        # """Info about the file"""

    def __repr__(self):
        """
        Representation of object
        :return: String representation of object.
        """
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)


class MultiJobLog(AMultiJobFile):
    """
    MultiJob log data container.
    """

    def __init__(self, path, file):
        super().__init__(path, file)


class MultiJobRes(AMultiJobFile):
    """
    MultiJob log data container.
    """

    def __init__(self, path, file):
        super().__init__(path, file)


class MultiJobConf(AMultiJobFile):
    """
    MultiJob conf data container.
    """

    def __init__(self, path, file):
        super().__init__(path, file)
