# -*- coding: utf-8 -*-
"""
MujtiJob data structure.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import time

from data.states import TaskStatus


class MultiJob:
    def __init__(self, preset):
        self.preset = preset
        self.state = MultiJobState(preset.name)


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
        self.qued_time = None
        """When MultiJob was qued"""
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

        self.updated = time.time()
        """Timestamp of last update from remote data"""

    def update(self, state):
        """
        Update state with received data
        :param state: Communication state data
        :return: None
        """
        self.qued_time = state.qued_time
        self.start_time = state.start_time
        self.run_interval = state.run_interval
        self.status = state.status
        self.known_jobs = state.known_jobs
        self.estimated_jobs = state.estimated_jobs
        self.finished_jobs = state.finished_jobs
        self.running_jobs = state.running_jobs
        # update timestamp
        self.updated = time.time()


class JobState:
    pass

