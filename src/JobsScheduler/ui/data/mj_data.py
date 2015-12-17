# -*- coding: utf-8 -*-
"""
MujtiJob data structure.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import os
import time

from communication import Installation
from data.states import TaskStatus, JobsState
from ui.data.preset_data import APreset


class MultiJob:
    def __init__(self, preset):
        self.preset = preset
        self.state = MultiJobState(preset.name)

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
        res_path = Installation.get_result_dir_static(self.preset.name)
        states = JobsState()
        states.load_file(res_path)
        return states.jobs

    def get_logs(self):
        """
        Scans log directory and returns log files.
        :return: List of MultiJobLog objects
        """
        log_path = Installation.get_mj_log_dir_static(self.preset.name)
        logs = []
        for file in os.listdir(log_path):
            if os.path.isfile(os.path.join(log_path, file)):
                log = MultiJobLog(log_path, file)
                logs.append(log)
        return logs

    def get_results(self):
        """
        Scans res directory and returns results files.
        :return: List of MultiJobRes objects
        """
        res_path = Installation.get_result_dir_static(self.preset.name)
        ress = []
        for file in os.listdir(res_path):
            if os.path.isfile(os.path.join(res_path, file)):
                res = MultiJobLog(res_path, file)
                ress.append(res)
        return ress

    def get_configs(self):
        """
        Scans res directory and returns config files.
        :return: List of MultiJobConf objects
        """
        conf_path = Installation.get_config_dir_static(self.preset.name)
        confs = []
        for file in os.listdir(conf_path):
            if os.path.isfile(os.path.join(conf_path, file)):
                conf = MultiJobLog(conf_path, file)
                confs.append(conf)
        return confs


class MultiJobState:
    """
    Data for current state of MultiJob
    """

    def __init__(self, name):
        """
        Default initialization.
        :param name: MultiJob name
        :return: None
        """
        self.name = name
        """Name of multijob"""
        self.insert_time = time.time()
        """When MultiJob was started"""
        self.queued_time = None
        """When MultiJob was queued"""
        self.start_time = None
        """When MultiJob was started"""
        self.run_interval = 0
        """MultiJob run time from start in second"""
        self.status = TaskStatus.none
        """MultiJob current status"""
        self.known_jobs = 0
        """Count of known jobs (minimal amount of jobs)"""
        self.estimated_jobs = 0
        """Estimated count of jobs"""
        self.finished_jobs = 0
        """Count of finished jobs"""
        self.running_jobs = 0
        """Count of running jobs"""

        self.update_time = None
        """When MultiJobState  was last updated"""

    def update(self, new_state):
        """
        Update new_state with received data
        :param new_state: Communication new_state data
        :return: None
        """
        # self.queued_time = new_state.queued_time
        # self.start_time = new_state.start_time
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


class MultiJobPreset(APreset):
    """
    MultiJob preset data container.
    """

    def __init__(self, name="Default MultiJob Preset Name"):
        """
        Default initialization.
        :return: None
        """
        super().__init__(name)
        self.analysis = ""
        """Path to analysis folder"""
        self.resource_preset = None
        """Selected resource preset"""
        self.pbs_preset = None
        """AdHoc PBS preset override"""
        self.log_level = logging.DEBUG
        """Logging level"""
        self.number_of_processes = "1"
        """Number of processes used by MultiJob"""

    def __repr__(self):
        """
        Representation of object
        :return: String representation of object.
        """
        return "%s(%r)" % (self.__class__.__name__, self.__dict__)


class MultiJobActions:
    @classmethod
    def run(cls, mj):
        """
        Reset times and remove previous results.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().run_interval = 0
        mj.get_state().queued_time = None
        mj.get_state().start_time = None
        mj.get_state().known_jobs = 0
        mj.get_state().estimated_jobs = 0
        mj.get_state().finished_jobs = 0
        mj.get_state().running_jobs = 0

        mj.get_state().set_status(TaskStatus.installation)

    @classmethod
    def pausing(cls, mj):
        """
        Changes status to pausing.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.pausing)

    @classmethod
    def paused(cls, mj):
        """
        Changes status to paused.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.paused)

    @classmethod
    def resuming(cls, mj):
        """
        Changes status to resuming.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.resuming)

    @classmethod
    def resumed(cls, mj):
        """
        Changes status to resumed.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.running)

    @classmethod
    def stopping(cls, mj):
        """
        Changes status to stopping.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.stopping)

    @classmethod
    def stopped(cls, mj):
        """
        Changes status to stopped.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.none)

    @classmethod
    def installation(cls, mj):
        """
        Changes status to installation.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().queued_time = time.time()

        mj.get_state().set_status(TaskStatus.installation)

    @classmethod
    def queued(cls, mj):
        """
        Changes status to queued and sets queued time.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().queued_time = time.time()

        mj.get_state().set_status(TaskStatus.queued)

    @classmethod
    def running(cls, mj):
        """
        Changes status to queued and sets queued time.
        :param mj: MultiJob instance
        :return:
        """
        if not mj.get_state().queued_time:
            mj.get_state().queued_time = time.time()
        mj.get_state().start_time = time.time()

        mj.get_state().set_status(TaskStatus.running)

    @classmethod
    def finished(cls, mj):
        """
        Changes status to finished.
        :param mj: MultiJob instance
        :return:
        """
        mj.get_state().set_status(TaskStatus.finished)
