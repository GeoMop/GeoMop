import logging
import copy
import data.transport_data as tdata
import data.communicator_conf as comconf
from .communicator import Communicator
from  communication.installation import  Installation
from communication.std_input_comm import StdInputComm
import threading
from  communication.exec_output_comm import  ExecOutputComm
import time

logger = logging.getLogger("Remote")

class JobsCommunicator(Communicator):
    """Class that add communicators properties to communication with job"""
    
    def __init__(self, init_conf, id=None , action_func_before=None, action_func_after=None, idle_func=None):
        self.conf = copy.deepcopy(init_conf)
        """Copy of communicator configuration use up to for job initialization"""
        if init_conf.output_type != comconf.OutputCommType.ssh:
            # socket based connection have output directly to jobs            
            init_conf.output_type = comconf.OutputCommType.none            
        super(JobsCommunicator, self).__init__(
                init_conf, id, action_func_before, action_func_after, self.job_idle_func)
        self.mj_name = init_conf.mj_name        
        """folder name for multijob data"""
        self.jobs = {}
        """Dictionary of jobs that is run by communicator"""
        self.job_outputs = {}
        """Dictionary of jobs outputs"""
        self._job_semafores = {}
        """Job semafore for guarding one run job action"""
        self.last_send_id = None 
        """Job id from which is send last message over ssh"""
        if idle_func is None:
            self.anc_idle_func = self.standart_idle_function
            """
            Ancestor idle function
           
            For job communicator is  called job_idle_function, that make 
            job specific action. If any job specific action is not pending, 
            user defined idle function in this variable is called .
            """
        else:
            self.anc_idle_func = idle_func
        
    def  standart_action_function_before(self, message):
        """before action function"""
        if message.action_type == tdata.ActionType.interupt_connection:
            self._interupt = True
            action = tdata.Action(tdata.ActionType.ok)
            return False, action.get_message()
        if message.action_type == tdata.ActionType.restore_connection:
            self.restore()
            action = tdata.Action(tdata.ActionType.ok)
            return False, action.get_message()
        if message.action_type == tdata.ActionType.installation:            
            resent, mess = super(JobsCommunicator, self).standart_action_function_before(message)
            if self.is_installed():
                logger.debug("Job application was started")
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
        if message.action_type == tdata.ActionType.interupt_connection:
            return None
        if message.action_type == tdata.ActionType.stop:
            # ToDo:: close all jobs 
            self.stop = True
            logger.info("Stop signal is received")
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        if message.action_type == tdata.ActionType.download_res:
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        return super(JobsCommunicator, self).standart_action_function_after(message,  response)

    def  job_idle_func(self):
        """
        Make job specific action. If is not action pending, run anc_idle_func
        
        For connection over ssh make:
            - Find next unconnected over socket job and send add_job message to it
              over remote. If job_conn akcion is returned, connect, and continue 
              connecion over socket
        For other connections make:
            - Find first unconnected job and try connect it

        Call standart communicator idle function. But only if long action is not 
        already processed it.
        """
        make_custom_action = True
        if self.conf.output_type == comconf.OutputCommType.ssh:
            pending_outputs = []
            next = 0
            for id in self.jobs:
                # connect
                if not self.job_outputs[id].isconnected() and self.job_outputs[id].initialized:
                    pending_outputs.append(id)
                    if id == self.last_send_id:
                        next = len(pending_outputs)
            if len(pending_outputs) > 0:
                if len(pending_outputs) == next:
                    next = 0
                id = pending_outputs[next]
                action=tdata.Action(tdata.ActionType.add_job)
                action.data.set_id(id)
                mess = action.get_message()
                self.last_send_id = id
                logger.debug("Before send")
                self.send_message(mess)
                mess = self.receive_message()
                if mess is not None and mess.action_type == tdata.ActionType.job_conn:
                    # connection over remote was established
                    self.job_outputs[id].host = mess.get_action().data.data['host']
                    self.job_outputs[id].port = mess.get_action().data.data['port']
                    self._connect_socket(self.job_outputs[id], 1)
                    make_custom_action = False
        else:
            for id in self.jobs:
                # connect
                if not self.job_outputs[id].isconnected() and self.job_outputs[id].initialized:
                    self._connect_socket(self.job_outputs[id], 1)
                    make_custom_action = False
            else:         
                for id in self.jobs:
                    # connect
                    if not self.job_outputs[id].connected and self.job_outputs[id].initialized:
                        self._connect_socket(self.job_outputs[id], 1)
                        make_custom_action = False
        if make_custom_action:
            self.anc_idle_func()

    def _exec_(self):
        """
        Exec for jobs_communicator don't make connection for
        actual job. Connectcions will be maked by add_job if is
        needed.
        """
        if self.conf.output_type == comconf.OutputCommType.ssh:
            super(JobsCommunicator, self)._exec_()
        
    def add_job(self, id, job):
        """Add job to dictionary, process it and make connection if is needed"""
        self.jobs[id] = job
        """Dictionary of jobs that is run by communicator"""
        self.job_outputs[id] = self.get_output(self.conf, id)
        self._job_semafores[id] = threading.Semaphore()
        
        self.job_outputs[id].installation.local_copy_path() # only copy path
        logger.debug("Starting job: " + id + " (" + type(self.job_outputs[id]).__name__ + ")")
        
        if self.conf.output_type == comconf.OutputCommType.ssh:
            self.job_outputs[id] = ExecOutputComm(self.conf.mj_name, self.conf.port)
            self.job_outputs[id].initialized = True
        else:
            self.job_outputs[id] = self.get_output(self.conf, id)
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
        if self.conf.output_type == comconf.OutputCommType.ssh:
            super(JobsCommunicator, self).install()
        else:
            # socket based connection only install libs
            if self.libs_env.install_job_libs:
                Installation.install_job_libs_static(self.conf.mj_name, self.conf.python_env, self.conf.libs_env)
            self._install_lock.acquire()
            self._instaled = True
            self._install_lock.release()
        
    def restore(self):
        """Restore connection chain to next communicator"""
        self.status.load()
        self.status.interupted=False
        self.status.save()
        logger.info("Multi Job Application " + self.communicator_name + " is restored")    
        
    def interupt(self):
        """Interupt connection chain to next communicator"""
        self.status.interupted=True        
        self.status.save()
        if self.input is not None:
            if not isinstance(self.input, StdInputComm):
                self.input.disconnect()
                time.sleep(10)
                self.input.connect()
        logger.info("Multi Job Application " + self.communicator_name + " is interupted")    
