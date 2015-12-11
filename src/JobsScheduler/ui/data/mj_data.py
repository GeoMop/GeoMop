# -*- coding: utf-8 -*-
"""
MujtiJob data structure.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import logging
import time

from data.states import TaskStatus
from ui.data.preset_data import APreset


class MultiJob:
    def __init__(self, preset):
        self.preset = preset
        self.state = MultiJobState(preset.name)
        self.logs = None
        self.jobs = None
        self.res = None
        self.conf = None

    def action_run(self):
        """
        Reset times and remove previous results.
        :return: None
        """
        # reset data
        # self.logs = None
        self.jobs = None
        # self.res = None
        # self.conf = None

        # reset times
        self.state.queued_time = None
        self.state.start_time = None

        # set status to installation
        self.change_status(TaskStatus.installation)

    def action_queued(self):
        """
        Changes status to queued and sets queued time.
        :return: None
        """
        self.state.queued_time = time.time()
        # set status to installation
        self.change_status(TaskStatus.queued)

    def action_running(self):
        """
        Changes status to queued and sets queued time.
        :return: None
        """
        if not self.state.queued_time:
            self.state.queued_time = time.time()
        self.state.start_time = time.time()
        # set status to installation
        self.change_status(TaskStatus.running)

    def update_state(self, new_state):
        """
        Update MultiJob status with received data.
        :param new_state: State object that updates current state.
        :return: None
        """
        self.state.update(new_state)

    def change_status(self, new_status):
        """
        Directly changes status of the MultiJob
        :param new_status: TaskStatus o replace current.
        :return: None
        """
        self.state.status = new_status


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

    def update(self, state):
        """
        Update state with received data
        :param state: Communication state data
        :return: None
        """
        # self.queued_time = state.queued_time
        # self.start_time = state.start_time
        self.run_interval = state.run_interval
        self.status = state.status
        self.known_jobs = state.known_jobs
        self.estimated_jobs = state.estimated_jobs
        self.finished_jobs = state.finished_jobs
        self.running_jobs = state.running_jobs


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


class JobState:
    pass
