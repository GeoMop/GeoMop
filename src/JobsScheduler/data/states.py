import json
import os
import logging
import time
from enum import IntEnum

logger = logging.getLogger("Remote")

class TaskStatus(IntEnum):
    """Action type"""
    installation = 0
    qued = 1
    running = 2
    stopping = 3
    ready = 4
    none = 5
    pausing = 6
    paused = 7
    resuming = 8
    stopped = 9

class MJState:
    def __init__(self, name, install=False):
        self.name = name
        """Name of multijob"""        
        self.insert_time = time.time()
        """when multiJob was started"""
        self.qued_time = None
        """when multiJob was qued"""
        self.start_time = None
        """when multiJob was started"""
        self.run_interval = 0
        """Job run time from start in second"""
        self.status = TaskStatus.none
        if install:
            self.status = TaskStatus.installation
        """multijob status"""
        self.known_jobs = 0
        """count of known jobs (minimal amout of jobs)"""
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
        self.qued_time = None
        """when Job was qued"""
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
        except Exception as error:
            logger.error("Load state error:" + str(error))
