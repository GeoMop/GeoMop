import json
import os
import logging
from enum import Enum

class TaskStatus(Enum):
    """Action type"""
    installation = 0
    qued = 1
    running = 2
    stoping = 3
    ready = 4
    none = 5

class MJState:
    def __init__(self, name):
        self.name = name
        """Name of multijob"""        
        self.insert_time = None
        """when multiJob was started"""
        self.qued_time = None
        """when multiJob was qued"""
        self.start_time = None
        """when multiJob was started"""
        self.run_interval = 0
        """Job run time from start in second"""
        self.status=TaskStatus.none
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
    def __init__(self, name):
        self.name = name
        """Name of job"""
        self.insert_time = None
        """when Job was started"""
        self.qued_time = None
        """when Job was qued"""
        self.start_time = None
        """when Job was started"""
        self.run_interval=0
        """Job run time from start in second"""
        self.status=TaskStatus.none
        """job status"""
        
class JobsState:
    def __init__(self):
        self.jobs=[]
        """array of jobs states"""

    def save_file(self, res_dir):
        """Job data serialization"""
        data = self.jobs
        file = os.path.join("jobs_states.json")
        try:
            with open(file, "w") as json_file:
                json.dump(data, json_file, indent=4, sort_keys=True)
        except Exception as error:
            logging.error("Save state error:" + error)
            raise error

    def load_file(self, res_dir):
        """Job data serialization"""       
        file = os.path.join("jobs_states.json")
        try:
            with open(file, "r") as json_file:
                data = json.load(json_file)
                self.jobs = data
        except Exception as error:
            logging.error("Save state error:" + error)
            raise error
        
        
