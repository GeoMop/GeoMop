import logging
import copy
import subprocess
import data.transport_data as tdata
import data.communicator_conf as comconf
from .communicator import Communicator
from  communication.installation import  Installation

class JobsCommunicator(Communicator):
    """Class that add communicators properties to communication with job"""
    
    def __init__(self, init_conf, id=None , action_func_before=None, action_func_after=None):
        self.conf = copy.deepcopy(init_conf)
        """Copy of communicator configuration use up to for job initialization"""
        init_conf.output_type = comconf.OutputCommType.none
        super(JobsCommunicator, self).__init__(init_conf, id, action_func_before, action_func_after)
        self.mj_name = init_conf.mj_name
        """folder name for multijob data"""
        self.jobs = {}
        """Dictionary of jobs that is run by communicator"""
        self.job_outputs = {}
        """Dictionary of jobs outputs"""        
        
    def  standart_action_funcion_before(self, message):
        """before action function"""
        if message.action_type == tdata.ActionType.installation:
            logging.debug("Job apllication began start")
            try:
                installation = Installation(self.mj_name)
                # installation.set_install_params("/opt/python/bin/python3.3", None)
                installation.local_copy_path()           
                subprocess.Popen(installation.get_args("job"))
                action = tdata.Action(tdata.ActionType.ok)
            except(OSError, ValueError) as err:
                logging.error("Start of job apllication raise error: " + str(err))
                action=tdata.Action(tdata.ActionType.error)
                action.data.data["msg"] = "Next communicator can not be run"        
            return False, True, action.get_message()
        if message.action_type == tdata.ActionType.stop:
            # processing in after function
            return False, False, None
        return super(JobsCommunicator, self).standart_action_funcion_before(message)
        
    def  mj_action_funcion_after(self, message,  response):
        """before action function"""
        if message.action_type == tdata.ActionType.stop:
            # ToDo:: close all jobs 
            self.stop = True
            logging.info("Stop signal is received")
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        return super(JobsCommunicator, self).standart_action_funcion_after(message,  response)
        
    def _exec_(self):
        """
        Exec for jobs_communicator don't make connection for
        actual job. Connectcions will be maked by add_job if is
        need.
        """
        pass
        
    def add_job(self, id, job):
        """Add job to dictionary, process it and make connection if is needed"""
        self.jobs[id] = job
        """Dictionary of jobs that is run by communicator"""
        self.job_outputs[id] = self.get_output(self.conf)
        self.job_outputs[id].exec_(self.next_communicator)
