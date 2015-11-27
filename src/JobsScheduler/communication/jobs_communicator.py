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
from data.states import JobsState, MJState, TaskStatus

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
        self.ready_jobs = {}
        """Dictionary of jobs that is ready"""
        self.job_outputs = {}
        """Dictionary of jobs outputs"""
        self._last_send_id = None 
        """Job id from which is send last message over ssh"""
        self._last_check_id = None
        """Job id from which is send last message over ssh"""
        self._mj_state = MJState(self.mj_name, True)
        self._state_running()
        """Multi Job state"""
        self._stopping = False        
        """if iapplication is stop before end"""
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
                logger.debug("MultiJob application was started")
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
            self._state_stopping()
            if len(self.jobs) > 0:
                self._stopping = True
                action = tdata.Action(tdata.ActionType.action_in_process)
                return action.get_message()                    
            self._state_stoped()
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
            - if stopping is true, try stop next processes
            - Find first unconnected job and try connect it

        Call standart communicator idle function. But only if long action is not 
        already processed it.
        """
        if self._stopping:
            id = self._get_next_id(self._last_check_id)
            # ToDo in pbs try stop qued processes over qsub
            if id is not None:
                self.jobs[id].state_stopping()
                action=tdata.Action(tdata.ActionType.stop)
                logger.debug("Stop message to running job " + id + " is sent")
                self.job_outputs[id].send(action.get_message())
                mess = self.job_outputs[id].receive()
                logger.debug("Answer to stop nessage is receive (" + str(mess) + ')')
                if mess is not None and mess.action_type == tdata.ActionType.ok:
                    self.ready_jobs[id] = self.jobs[id]
                    self.jobs[id].state_stopped()
                    self.job_outputs[id].disconnect()
                    del self.jobs[id]
                    del self.job_outputs[id]
            return
        make_custom_action = True
        if self.conf.output_type == comconf.OutputCommType.ssh:
            id = self._get_next_id( self._last_send_id, False)
            if id is not None:
                action=tdata.Action(tdata.ActionType.add_job)
                action.data.set_id(id)
                mess = action.get_message()
                self._last_send_id = id
                self.send_message(mess)
                mess = self.receive_message()
                if mess is not None and mess.action_type == tdata.ActionType.job_conn:
                    # connection over remote was established
                    self.jobs[id].state_start()
                    self.job_outputs[id].host = mess.get_action().data.data['host']
                    self.job_outputs[id].port = mess.get_action().data.data['port']
                    self._connect_socket(self.job_outputs[id], 1)
                    make_custom_action = False
                    self._job_running()
        else:
            for id in self.jobs:
                # connect
                if not self.job_outputs[id].isconnected() and self.job_outputs[id].initialized:
                    self.jobs[id].state_start()
                    self._connect_socket(self.job_outputs[id], 1)
                    make_custom_action = False
                    self._job_running()
        if make_custom_action:
            # get status
            id = self._get_next_id(self._last_check_id)
            if id is not None:    
                action=tdata.Action(tdata.ActionType.get_state)
                logger.debug("Get job status message to " + id + " is sent")
                self.job_outputs[id].send(action.get_message())
                mess = self.job_outputs[id].receive()
                logger.debug("Answer to status nessage is receive (" + str(mess) + ')')
                self._last_check_id = id
                if mess is not None and mess.action_type == tdata.ActionType. job_state:
                    if mess.get_action().data.data['ready']:
                        action=tdata.Action(tdata.ActionType.stop)
                        logger.debug("Stop message to ready job " + id + " is sent")
                        self.job_outputs[id].send(action.get_message())
                        mess = self.job_outputs[id].receive()
                        logger.debug("Answer to stop nessage is receive (" + str(mess) + ')')
                        if mess is not None and mess.action_type == tdata.ActionType.ok:
                            self.ready_jobs[id] = self.jobs[id]
                            self.jobs[id].state_ready()
                            self.job_outputs[id].disconnect()
                            del self.jobs[id]
                            del self.job_outputs[id]
                            self._job_ready()
        if make_custom_action:
            self.anc_idle_func()
            
    def _get_next_id(self, last_id, connected=True):
        """
        Communication with jobs is make in idle function. All operation is make
        cyrcularly for one job that is in the order. This function return job id that 
        is in the order. In idle function is can't be made long actions.
        """
        id = None
        pending_outputs = []
        next = 0
        for id in self.jobs:
            if connected:
                state_ok = self.job_outputs[id].isconnected()
            else:
                state_ok = not self.job_outputs[id].isconnected() and self.job_outputs[id].initialized
            if state_ok:                
                pending_outputs.append(id)
                if id == last_id:
                    next = len(pending_outputs)
        if len(pending_outputs) > 0:
            if len(pending_outputs) == next:
                next = 0
            id = pending_outputs[next]
        return id

    def  get_jobs_states(self):
        """return state all jobs"""
        states = JobsState()
        for id in self.ready_jobs:
            states.jobs.append(self.ready_jobs[id].get_state())
        for id in self.jobs:
            states.jobs.append(self.jobs[id].get_state())
        return states

    def _exec_(self):
        """
        Exec for jobs_communicator don't make connection for
        actual job. Connectcions will be maked by add_job if is
        needed.
        """
        if self.conf.output_type == comconf.OutputCommType.ssh:
            super(JobsCommunicator, self)._exec_()
        self._state_ready()
        
    def add_job(self, id, job):
        """Add job to dictionary, process it and make connection if is needed"""
        self.jobs[id] = job
        """Dictionary of jobs that is run by communicator"""
        if self.conf.output_type == comconf.OutputCommType.ssh:
            self.job_outputs[id] = ExecOutputComm(self.conf.mj_name, self.conf.port)
            logger.debug("Starting job: " + id + " (" + type(self.job_outputs[id]).__name__ + ")")
            self.job_outputs[id].initialized = True
        else:
            self.job_outputs[id] = self.get_output(self.conf, id)
            self.job_outputs[id].installation.local_copy_path() # only copy path
            logger.debug("Starting job: " + id + " (" + type(self.job_outputs[id]).__name__ + ")")
            t = threading.Thread(target= self._run_action, 
                  args=( self.job_outputs[id].exec_,id))
            t.daemon = True            
            t.start()
        self.jobs[id].state_qued()
        
    def _run_action(self, action, id):
        """
        Run action. If action is ready, job will be connected.
        This is signal for app, that may safetly continue, and
        lock is not needed.
        """        
        action(self.next_communicator,self.mj_name, id)
        
    def install(self):
        """make installation"""
        if self.conf.output_type == comconf.OutputCommType.ssh:
            super(JobsCommunicator, self).install()
            self.send_long_action(tdata.Action(tdata.ActionType.installation))
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
        
    def _state_running(self):
        """change state to running"""
        self._mj_state.start_time = time.time()
        self._mj_state.status = TaskStatus.running
       
    def _state_ready(self):
        """change state to ready"""
        self._mj_state.run_interval = int(time.time() - self._mj_state.start_time )
        self._mj_state.status = TaskStatus.ready
        
    def _state_stopping(self):
        """change state to stopping"""
        self._mj_state.run_interval = int(time.time() - self._mj_state.start_time) 
        self._mj_state.status = TaskStatus.stopping
        
    def _state_stoped(self):
        """change state to stoped"""
        self._mj_state.status = TaskStatus.stopped
    
    def get_state(self):
        """change state to qued"""
        if self._mj_state.status == TaskStatus.running:
            self._mj_state.run_interval = int(time.time() - self._mj_state.start_time)
        new_state = copy.deepcopy(self._mj_state)
        return new_state
        
    def set_start_jobs_count(self, known, estimated):
        "Set count of processes at start of application"
        self._mj_state.known_jobs = known
        self._mj_state.estimated_jobs = estimated

    def _job_running(self):
        "One process is moved from known to running state"
        self._mj_state.known_jobs -= 1
        self._mj_state.running_jobs += 1
        
    def _job_ready(self):
        "One process is moved from running to ready state"
        self._mj_state.running_jobs -= 1
        self._mj_state.finished_jobs += 1
        if self._mj_state.known_jobs == 0 and self._mj_state.estimated_jobs == 0 and \
            self._mj_state.running_jobs == 0:
            self._state_ready()
