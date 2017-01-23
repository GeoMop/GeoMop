import json
import os
import logging
import time
from enum import IntEnum

logger = logging.getLogger("Remote")


class TaskStatus(IntEnum):
    """
    Action type ('start app action' is action required, if state is in start of application)
    """
    installation = 0
    """
    Multijob is installed
    :permited actions: resume, stop (but only if js_services is allready installed, 
    in gui is action permited and wait ComManager )
    :start app action: terminate job and set error message
    """
    queued = 1
    """
    js_services or job wait in pbs queue
    :permited actions: resume, stop (but only if js_services is allready installed, 
    in gui is action permited and wait ComManager )
    :start app action: terminate job and set error message
    """    
    running = 2
    """
    running state
    :permited actions: resume,stop
    :start app action: resume job
    """
    stopping = 3
    """
    Multijob is about stopping
    :permited actions: no
    :start app action: terminate job
    """
    ready = 4
    """
    Job is finished
    :permited actions: no
    :start app action: resume
    """
    none = 5
    """
    MultiJob is New or state is unknown
    :permited actions: Run, Delete
    :start app action: OK
    """
    pausing = 6
    """
    MultiJob is about pausing
    :permited actions: no
    :start app action: resume job
    """
    paused = 7
    """
    MultiJob is paused (only debug or switch off application)
    :permited actions: no
    :start app action: resume job
    """
    resuming = 8
    """
    MultiJob is about resuming
    :permited actions: no
    :start app action: resume job
    """    
    stopped = 9
    """
    MultiJob was stopped by user
    :permited actions: delete
    :start app action: no
    """
    finished = 10
    """
    MultiJob was finished, all is OK
    :permited actions: delete
    :start app action: no
    """
    interrupted = 11
    """
    No respons, connection with application was interupted
    :permited actions: no
    :start app action: resume
    """
    error = 12
    """
    MultiJob was finished with error
    :permited actions: delete
    :start app action: no
    """
    deleting = 13
    """
    MultiJob delete attempt is processed
    :permited actions: no
    :start app action: no (rename to error or OK)
    
    This state is only for gui
    """

    def __str__(self):
        """Return string representation."""
        return _TASK_STATUS_DISPLAY_NAMES[self]


_TASK_STATUS_DISPLAY_NAMES = {
    TaskStatus.error: 'Error',
    TaskStatus.finished: 'Finished',
    TaskStatus.installation: 'Installation',
    TaskStatus.interrupted: 'No response',
    TaskStatus.none: 'New',
    TaskStatus.paused: 'Paused',
    TaskStatus.pausing: 'Pausing',
    TaskStatus.queued: 'Queued',
    TaskStatus.ready: 'Ready',
    TaskStatus.resuming: 'Resuming',
    TaskStatus.running: 'Running',
    TaskStatus.stopped: 'Stopped',
    TaskStatus.stopping: 'Stopping', 
    TaskStatus.deleting: 'Deleting'
}


class MultijobActions(IntEnum):
    """Possible actions for selected multijob."""
    delete_remote = 0
    delete = 1
    reuse = 2
    stop = 3
    terminate = 4
    resume = 6


TASK_STATUS_PERMITTED_ACTIONS = set([
    (TaskStatus.error, MultijobActions.delete_remote),
    (TaskStatus.error, MultijobActions.delete),
    (TaskStatus.finished, MultijobActions.delete_remote),
    (TaskStatus.finished, MultijobActions.delete),
    (TaskStatus.installation, MultijobActions.resume),
    (TaskStatus.installation, MultijobActions.stop),
    (TaskStatus.none, MultijobActions.delete), 
    (TaskStatus.queued, MultijobActions.resume),
    (TaskStatus.queued, MultijobActions.stop),
    (TaskStatus.running, MultijobActions.resume),
    (TaskStatus.running, MultijobActions.stop),
    (TaskStatus.stopped, MultijobActions.delete), 
    (TaskStatus.stopped, MultijobActions.delete_remote)
])


TASK_STATUS_STARTUP_ACTIONS = {
    TaskStatus.error: None,
    TaskStatus.finished: None,
    TaskStatus.installation: MultijobActions.terminate,
    TaskStatus.interrupted: MultijobActions.resume,
    TaskStatus.none: None,
    TaskStatus.paused: MultijobActions.resume,
    TaskStatus.pausing: MultijobActions.resume,
    TaskStatus.queued: MultijobActions.terminate,
    TaskStatus.ready: None,
    TaskStatus.resuming: MultijobActions.resume,
    TaskStatus.running: MultijobActions.resume,
    TaskStatus.stopped: None,
    TaskStatus.stopping: MultijobActions.terminate, 
    TaskStatus.deleting: None
}


class MJState:
    def __init__(self, name, install=False):
        self.name = name
        """Name of multijob"""        
        self.insert_time = time.time()
        """when multiJob was started"""
        self.queued_time = None
        """when multiJob was queued"""
        self.start_time = None
        """when multiJob was started"""
        self.run_interval = 0
        """Job run time from start in second"""
        self.status = TaskStatus.none
        if install:
            self.status = TaskStatus.installation
        """multijob status"""
        self.known_jobs = 0
        """count of known jobs (minimal amount of jobs)"""
        self.estimated_jobs = 0
        """estimated count of jobs"""
        self.finished_jobs = 0
        """count of finished jobs"""
        self.running_jobs = 0
        """count of running jobs"""


class JobState:
    def __init__(self, name, install=False):
        self.name = name
        """Name of job"""
        self.insert_time = time.time()
        """when Job was started"""
        self.queued_time = None
        """when Job was queued"""
        self.start_time = None
        """when Job was started"""
        self.run_interval = 0
        """Job run time from start in second"""
        self.status = TaskStatus.none
        """job status"""
        if install:
            self.status = TaskStatus.installation


class JobsState:
    def __init__(self):
        self.jobs = []
        """array of jobs states"""

    def save_file(self, res_dir):
        """Job data serialization"""
        data = []
        for job in self.jobs:
            job.status=job.status.value
            data.append(job.__dict__)
        path = os.path.join(res_dir,"state")
        if not os.path.isdir(path):
            os.makedirs(path)
        file = os.path.join(path,"jobs_states.json")
        try:
            with open(file, "w") as json_file:
                json.dump(data, json_file, indent=4, sort_keys=True)
        except Exception as error:
            logger.error("Save state error:" + str(error))

    def load_file(self, res_dir):
        """Job data serialization"""       
        file = os.path.join(res_dir,"state","jobs_states.json")                   
        try:
            with open(file, "r") as json_file:
                data = json.load(json_file)
                for job in data:
                    obj = JobState(job['name'])
                    obj.__dict__=job
                    self.jobs.append(obj)                
        except:
            pass
