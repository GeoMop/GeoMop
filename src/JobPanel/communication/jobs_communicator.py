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
from data.job import  Job

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
        self._init_counts = None        
        """If this variable is set, initialization of mj state in next communicator
        is needed. This variable is :class:`data.transport_data.StartCountsData` 
        structure"""
        self.ready = False
        """Communicator is ready for job running"""
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
        if message.action_type == tdata.ActionType.restore_connection or \
            message.action_type == tdata.ActionType.restore:
            if not self._restored:
                res = self.restore(message.action_type == tdata.ActionType.restore)
                self.ready = message.action_type != tdata.ActionType.restore
                if res is not None:
                    # restore retur error
                    logger.warning("Restore error: {0}".format(res))
                    action=tdata.Action(tdata.ActionType.error)
                    action.data.data["msg"] = res
                    action.data.data["severity"] = 5
                    if self.status.next_started:
                        action.data.data["severity"] = 3
                else:
                    if  message.action_type == tdata.ActionType.restore and \
                        self.conf.output_type == comconf.OutputCommType.ssh and \
                        not self.conf.direct_communication:
                        # repeate in next request for remote
                        action = tdata.Action(tdata.ActionType.action_in_process)
                    else:
                        action = tdata.Action(tdata.ActionType.ok)                    
                return False, action.get_message()
        if message.action_type == tdata.ActionType.installation:            
            resent, mess = super(JobsCommunicator, self).standart_action_function_before(message)
            if mess is not None and mess.action_type == tdata.ActionType.error:
                return resent, mess
            if self.is_installed():
                logger.debug("MultiJob application was started")
                action = tdata.Action(tdata.ActionType.ok)
                self.ready = True
                return False, action.get_message()                        
            if mess is not None and mess.action_type == tdata.ActionType.install_in_process:
                # renew install state to installation
                mess = tdata.Action(tdata.ActionType.install_in_process).get_message()
            return resent, mess
        if message.action_type == tdata.ActionType.download_res:
            if self.conf.output_type == comconf.OutputCommType.ssh and \
               not self.conf.direct_communication:
                # resend to ssh and after delete in after function
                return True, None
            else:
                # delete in after function
                return False, None
        if message.action_type == tdata.ActionType.delete:
            if self.conf.output_type != comconf.OutputCommType.ssh or \
               self.conf.direct_communication:
                return False, None
        if message.action_type == tdata.ActionType.stop:
            # processing in after function
            if self.conf.output_type != comconf.OutputCommType.ssh:
                return False, None
        return super(JobsCommunicator, self).standart_action_function_before(message)
        
    def  standart_action_function_after(self, message,  response):
        """before action function"""
        if message.action_type == tdata.ActionType.interupt_connection:
            return None
        if message.action_type == tdata.ActionType.stop or \
            message.action_type == tdata.ActionType.delete:
            self._state_stopping()
            if len(self.jobs) > 0:
                self._stopping = True
                logger.debug("{0} jobs is running during stoping".format(str(len(self.jobs))))
                action = tdata.Action(tdata.ActionType.action_in_process)
                return action.get_message()    
            if response is not None and \
                response.action_type == tdata.ActionType.action_in_process:
                return response
            self._state_stoped()
            self.stop = True
            if message.action_type != tdata.ActionType.delete:
                logger.info("Stop signal is received")                
            else:
                self.delete()
                logger.info("Delete signal is received")            
            if (response is None or \
                response.action_type != tdata.ActionType.ok) and \
                self.status.next_installed:
                self.terminate_connections()
            action = tdata.Action(tdata.ActionType.ok)
            return action.get_message()
        if message.action_type == tdata.ActionType.download_res:           
            if self.conf.output_type != comconf.OutputCommType.ssh or \
               self.conf.direct_communication:
                action = tdata.Action(tdata.ActionType.ok)
                self._try_finish_jobs()                
                return action.get_message()
        return super(JobsCommunicator, self).standart_action_function_after(message,  response)

    def  job_idle_func(self):
        """
        Make job specific action. If is not action pending, run anc_idle_func
        
        For connection over ssh make:
            - Find next unconnected over socket job and send add_job message to it
              over remote. If socket_conn akcion is returned, connect, and continue 
              connecion over socket
        For other connections make:
            - if stopping is true, try stop next processes
            - Find first unconnected job and try connect it

        Call standart communicator idle function. But only if long action is not 
        already processed it.
        """
        if self._stopping:
            if self.conf.output_type == comconf.OutputCommType.ssh and \
                not self.conf.direct_communication:
                self.jobs.clear()
                self.job_outputs.clear()
                return
            else:
                id = self._get_next_id(self._last_check_id)
                # ToDo in pbs try stop queued processes over qsub
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
                        self.delete_connection(id)
                        del self.jobs[id]
                        del self.job_outputs[id]
                return
        make_custom_action = True
        if self.conf.output_type == comconf.OutputCommType.ssh:
            if not self.conf.direct_communication:
                if self._init_counts is not None:
                    logger.debug("Indirect communication over SSH")
                    action=tdata.Action(tdata.ActionType.set_start_jobs_count)
                    action.data = self._init_counts
                    mess = action.get_message()
                    self.send_message(mess)
                    mess = self.receive_message()
                    if mess is not None and mess.action_type == tdata.ActionType.ok:
                        self._init_counts = None
                    make_custom_action = False
                else:
                    for id in self.jobs:
                        if self.jobs[id] is False:
                            action=tdata.Action(tdata.ActionType.add_job)
                            action.data.set_id(id)
                            mess = action.get_message()
                            self._last_send_id = id
                            self.send_message(mess)
                            mess = self.receive_message()
                            if mess is not None and mess.action_type == tdata.ActionType.ok:
                                self.jobs[id] = True
                                make_custom_action = False
                                break
            else:
                id = self._get_next_id( self._last_send_id, False)
                if id is not None:
                    action=tdata.Action(tdata.ActionType.add_job)
                    action.data.set_id(id)
                    mess = action.get_message()
                    self._last_send_id = id
                    self.send_message(mess)
                    mess = self.receive_message()
                    if mess is not None and mess.action_type == tdata.ActionType.socket_conn:
                        # connection over remote was established
                        self.jobs[id].state_start()
                        self.job_outputs[id].host = mess.get_action().data.data['host']
                        self.job_outputs[id].port = mess.get_action().data.data['port']
                        if self._connect_socket(self.job_outputs[id], 1):
                            self._job_running()
                            self.save_connection(self.job_outputs[id].host, self.job_outputs[id].port, id)
                        make_custom_action = False                       
        else:
            for id in self.jobs:
                # connect
                if not self.job_outputs[id].isconnected() and self.job_outputs[id].initialized:
                    self.jobs[id].state_start()
                    if  self._connect_socket(self.job_outputs[id], 1):
                        self._job_running()
                        self.save_connection(self.job_outputs[id].host, self.job_outputs[id].port, id)
                    make_custom_action = False                    
        if make_custom_action:
            # get status
            if self.conf.output_type != comconf.OutputCommType.ssh or \
               self.conf.direct_communication:                   
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
                            ret_code = mess.get_action().data.data["return_code"]
                            action=tdata.Action(tdata.ActionType.stop)
                            logger.debug("Stop message to ready job " + id + " is sent")
                            self.job_outputs[id].send(action.get_message())
                            mess = self.job_outputs[id].receive()
                            logger.debug("Answer to stop nessage is receive (" + str(mess) + ')')
                            if mess is not None and mess.action_type == tdata.ActionType.ok:
                                self.ready_jobs[id] = self.jobs[id]
                                if ret_code==0:
                                    self.jobs[id].state_ready()
                                else:
                                    self.jobs[id].state_error()
                                self.job_outputs[id].disconnect()
                                if self.conf.output_type != comconf.OutputCommType.ssh:
                                    self.delete_connection(id)                                    
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
        ret = None
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
            ret = pending_outputs[next]
        return ret

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
        self._state_running()
        
    def add_job(self, id):
        """Add job to dictionary, process it and make connection if is needed"""
        if self.conf.output_type == comconf.OutputCommType.ssh:  # if is remote
            if self.conf.direct_communication:
                # remote only runs the job; then the job communicates over socket
                self.jobs[id] = Job(id)
                self.job_outputs[id] = ExecOutputComm(self.conf.mj_name, self.conf.port)
                logger.debug("Starting job: " + id + " (" + type(self.job_outputs[id]).__name__ + ")")
                self.job_outputs[id].initialized = True
                self.jobs[id].state_queued()
            else:
                self.jobs[id] = False
                self.job_outputs[id] = None                
        else:
            self.jobs[id] = Job(id)
            self.job_outputs[id] = self.get_output(self.conf,self.mj_name, self.an_name, id)
            self.job_outputs[id].installation.local_copy_path() # only copy path
            logger.debug("Starting job: " + id + " (" + type(self.job_outputs[id]).__name__ + ")")
            t = threading.Thread(target= self._run_action, 
                  args=( self.job_outputs[id].exec_,id))
            t.daemon = True            
            t.start()
            self.jobs[id].state_queued()
        
    def _run_action(self, action, id):
        """
        Run action. If action is ready, job will be connected.
        This is signal for app, that may safetly continue, and
        lock is not needed.
        """        
        action(self.next_communicator, id)
    
    def download(self):    
        self._try_finish_jobs()
        super(JobsCommunicator, self).download()        
        
    def install(self, unlock=True):
        """make installation"""
        if self.conf.output_type == comconf.OutputCommType.ssh:
            super(JobsCommunicator, self).install(False)
            sec = time.time() + 600
            message = tdata.Action(tdata.ActionType.installation).get_message()
            mess = None
            while sec > time.time():
                self.send_message(message)
                mess = self.receive_message(120)
                if mess is None:
                    break
                if not mess.action_type == tdata.ActionType.install_in_process:
                    break
                time.sleep(10)            
        else:
            # socket based connection only install libs
            if self.libs_env.install_job_libs:
                Installation.install_job_libs_static(self.conf.mj_name, self.an_name, self.conf.python_env, self.conf.libs_env)
        if unlock:
            self._install_lock.acquire()
            self._instaled = True
            self._install_lock.release()
        
    def restore(self, recreate):
        """Restore connection chain to next communicator"""
        self.status.load()
        if recreate and \
            self.conf.output_type == comconf.OutputCommType.ssh and \
            not self.conf.direct_communication:
            if not self.output.isconnected():
                try:
                    self.output.connect()
                    self.output.exec_(self.next_communicator, self.id)
                except Exception as err:
                    return "Can't create ssh connection ({0})".format(str(err))          
        self.status.interupted=False
        self.status.save()
        self._restored = True
        logger.info("Application " + self.communicator_name + " is restored")    
        
    def interupt(self):
        """Interupt connection chain to next communicator"""
        self.status.interupted=True        
        self.status.save()
        logger.info("Application " + self.communicator_name + " is interupted")
        if self.input is not None:
            if not isinstance(self.input, StdInputComm):
                self.input.disconnect()
                time.sleep(10)
                self.input.connect()          
       
    def terminate_connections(self):
        """
        send terminate message to all recorded connections, and delete connections files
        
        After all function try kill next communicator (if next communicator is exec and was restored
        killing fails, but previous action should be functional - restore is possible only for active 
        connections)
        """
        super(JobsCommunicator, self).terminate_connections()
        for id in self.jobs:
            self.job_outputs[id].kill_next()
        
    def _state_running(self):
        """change state to running"""
        self._mj_state.start_time = time.time()
        self._mj_state.run_interval = int(time.time() - self._mj_state.start_time) 
        self._mj_state.status = TaskStatus.running
       
    def _state_ready(self):
        """change state to ready"""
        self._mj_state.run_interval = int(time.time() - self._mj_state.start_time )
        self._mj_state.status = TaskStatus.ready
       
    def _state_stopping(self):
        """change state to stopping"""        
        self._mj_state.status = TaskStatus.stopping
        
    def _state_stoped(self):
        """change state to stoped"""
        self._mj_state.status = TaskStatus.stopped
    
    def get_state(self):
        """change state to queued"""
        if self._mj_state.status == TaskStatus.running:
            self._mj_state.run_interval = int(time.time() - self._mj_state.start_time)
        new_state = copy.deepcopy(self._mj_state)
        return new_state
        
    def set_start_jobs_count(self, known, estimated):
        "Set count of processes at start of application"
        if self.conf.output_type == comconf.OutputCommType.ssh and \
            not self.conf.direct_communication:
            self._init_counts = tdata.StartCountsData()
            self._init_counts.set_data(known, estimated)
        else:
            self._mj_state.known_jobs = known
            self._mj_state.estimated_jobs = estimated
            if known==0 and estimated==0: 
                self._state_ready()

    def _job_running(self):
        "One process is moved from known to running state"
        self._mj_state.known_jobs -= 1
        self._mj_state.running_jobs += 1
        
    def _job_ready(self):
        "One process is moved from running to ready state"
        self._mj_state.running_jobs -= 1
        self._mj_state.finished_jobs += 1
        if self._mj_state.known_jobs <= 0 and self._mj_state.estimated_jobs <= 0 and \
            self._mj_state.running_jobs <= 0:
            self._state_ready()
            
    def _try_finish_jobs(self):
        "If job is ready and data is downloaded, set job to finish state"
        for id in self.ready_jobs:
            self.ready_jobs[id].state_ready_to_finish()
