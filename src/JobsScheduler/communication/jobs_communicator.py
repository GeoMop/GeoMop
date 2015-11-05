import logging
import copy
import data.transport_data as tdata
import data.communicator_conf as comconf
from .communicator import Communicator
from  communication.installation import  Installation
import threading

class JobsCommunicator(Communicator):
    """Class that add communicators properties to communication with job"""
    
    def __init__(self, init_conf, id=None , action_func_before=None, action_func_after=None, idle_func=None):
        self.conf = copy.deepcopy(init_conf)
        """Copy of communicator configuration use up to for job initialization"""
        init_conf.output_type = comconf.OutputCommType.none
        super(JobsCommunicator, self).__init__(init_conf, id, action_func_before, action_func_after, idle_func)
        self.mj_name = init_conf.mj_name
        """folder name for multijob data"""
        self.jobs = {}
        """Dictionary of jobs that is run by communicator"""
        self.job_outputs = {}
        """Dictionary of jobs outputs"""
        self._job_semafores = {}
        """Job semafore for guarding one run job action"""
        
    def  standart_action_function_before(self, message):
        """before action function"""
        if message.action_type == tdata.ActionType.installation:            
            resent, mess = super(JobsCommunicator, self).standart_action_function_before(message)
            if self.is_installed():
                logging.debug("Job application was started")
                action = tdata.Action(tdata.ActionType.ok)
                return False, action.get_message()
            return resent, mess
        if message.action_type == tdata.ActionType.download_res:
            # processing in after function
            return False, None
        if message.action_type == tdata.ActionType.stop:
            # processing in after function
            return False, None
        return super(JobsCommunicator, self).standart_action_function_before(message)
        
    def  standart_action_function_after(self, message,  response):
        """before action function"""
        if message.action_type == tdata.ActionType.stop:
            # ToDo:: close all jobs 
            self.stop = True
            logging.info("Stop signal is received")
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        if message.action_type == tdata.ActionType.download_res:
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        return super(JobsCommunicator, self).standart_action_function_after(message,  response)
        
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
        self.job_outputs[id] = self.get_output(self.conf, id)
        self._job_semafores[id] = threading.Semaphore()
        self.job_outputs[id].install() # only copy path
        
        logging.debug("Starting job: " + id + " (" + type(self.job_outputs[id]).__name__ + ")")
        t = threading.Thread(target= self._run_action, 
              args=( self.job_outputs[id].exec_,id, self._job_semafores[id]))
        t.daemon = True
        t.start()
        
    def _run_action(self, action, id, semafore):
        """Run action guardet by semafore"""        
        semafore.acquire()
        action(self.next_communicator,self.mj_name, id)
        semafore.release()
        
    def install(self):
        """make installation"""
        if self.libs_env.install_job_libs:
            Installation.install_job_libs_static(self.conf.mj_name, self.conf.python_env, self.conf.libs_env)
        self._install_lock.acquire()
        self._instaled = True
        self._install_lock.release()
