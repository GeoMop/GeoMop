import threading
import time
import copy
from data.states import JobState, TaskStatus


class Job:
    def __init__(self, name):
        self._data_lock = threading.Lock()
        """Lock for job data"""
        self._state = JobState(name, True)
        """Job state"""

    def state_queued(self):
        """change state to queued"""
        self._data_lock.acquire()
        self._state.queued_time = time.time()
        self._state.status = TaskStatus.queued
        self._data_lock.release()
        
    def state_start(self):
        """change state to running"""
        self._data_lock.acquire()
        self._state.start_time = time.time()
        self._state.status = TaskStatus.running
        self._data_lock.release()
        
    def state_ready(self):
        """change state to ready"""
        self._data_lock.acquire()
        self._state.run_interval = int(time.time() - self._state.start_time)
        self._state.status = TaskStatus.ready
        self._data_lock.release()

    def state_error(self):
        """change state to error"""
        self._data_lock.acquire()
        self._state.run_interval = int(time.time() - self._state.start_time)
        self._state.status = TaskStatus.error
        self._data_lock.release()

    def state_stopping(self):
        """change state to stopping"""
        self._data_lock.acquire()
        self._state.run_interval = int(time.time() - self._state.start_time )
        self._state.status = TaskStatus.stopping
        self._data_lock.release()
        
    def state_stopped(self):
        """change state to stoped"""
        self._data_lock.acquire()
        self._state.status = TaskStatus.stopped
        self._data_lock.release()
    
    def get_state(self):
        """change state to queued"""
        self._data_lock.acquire()
        if self._state.status == TaskStatus.running:
            self._state.run_interval = int(time.time() - self._state.start_time)
        new_state = copy.deepcopy(self._state)
        self._data_lock.release()
        return new_state

