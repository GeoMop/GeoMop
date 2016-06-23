import threading
import time
import logging
import os
import data.transport_data as tdata
from data.states import TaskStatus
from ui.data.mj_data import MultiJobState
from  communication.installation import __install_dir__

class ComWorker(threading.Thread):   
    """
    Class created own thread for installation, communication and
    cancelling next communicators.
    """
    def __init__(self, key, com):            
        super().__init__(name=com.mj_name)
        self._com = com
        """created Communicator for mj"""
        self._key = key
        """mj key"""
        self.__state_lock = threading.Lock()
        """lock for all next state variables, that use both threads"""
        self.__start = False
        """start job"""
        self.__start_state = TaskStatus.installation
        """start job state"""
        self.__running = False
        """mj run"""
        self.__starting = False
        """starting job"""
        self.__error_state = False
        """Error is occured, communication is stopped"""
        self.__error = None
        """error message"""
        self._ok_cancelling_state = None
        """
        Communicator state, that will has after successful cancelling.
        If this state is error, self.__error_state will be set to True
        """
        self._last_state = MultiJobState(com.mj_name) 
        """last mj state"""
        self.__state = None
        """mj state for return"""
        self.__downloaded = False
        """mj files is updated"""
        self.__stop = False
        """stop job"""
        self.__terminate = False
        """terminate job"""
        self.__finish = False
        """terminate job"""
        self.__pause = False
        """pause job"""
        self.__cancelling = False
        """cancelling job"""
        self.__cancelled = False
        """cancelled job"""
        self.__download = False
        """download files"""
        self.__get_state = False
        """get mj state"""
        self._counter = 0
        """planning counter (in main thread, not lock)"""
        
    def get_last_results(self, is_current):
        """
        return tupple (state, error, jobs_downloaded, results_downloaded , logs_downloaded)
        if new state is not known return None
        if new files is not downloaded return None
        
        parameters:
        :param bool is_current: is job selected in gui
        """
        self._counter += 1
        if is_current:
            if self._counter%2==0:
                self.__get_state = True
            if (self._counter%6+1)==0:
                self.__download = True
        else:
            if self._counter%4==0:
                self.__get_state = True
            if (self._counter%12+1)==0:
                self.__download = True
        state = None
        if self.__state is not None:
            state = self.__state
            self._last_state = self.__state
            self.__state = None 
        downloaded = self.__downloaded
        self.__downloaded = False
        error = None
        if self.__error is not None:
            error = self.__error
            self.__error = None
        return state,  error, downloaded, downloaded, downloaded
        
    def start_mj(self):
        """start communication"""
        self.start()
        self.__state_lock.acquire()
        self.__start = True
        self.__starting = True
        self.__state_lock.release()

    def get_start_state(self):
        """return instalation state"""
        self.__state_lock.acquire()
        state = self.__start_state
        self.__state_lock.release()
        return state
        
    def resume(self):
        """resume communication"""
        
    def is_started(self):
        """return if communication is started"""
        res = False
        self.__state_lock.acquire()
        if not self.__starting and not self.__start and \
            not self.__error_state and self.__running:
            res = True
        self.__state_lock.release()
        return res
        
    def is_interupted(self):
        """return if communication is interupted"""
        return False
        
    def is_error(self):
        """
        Return if communication is ended with error.
        If True is return thrad is stopped
        """        
        self.__state_lock.acquire()
        res = self.__error_state
        self.__state_lock.release()
        return res
        
    def stop(self):
        """stop communicator"""
        self.__state_lock.acquire()
        self.__stop = True
        self.__cancelling = True
        self._ok_cancelling_state = TaskStatus.stopped
        self.__state_lock.release()

    def finish(self):
        """download data and stop communicator"""
        self.__state_lock.acquire()
        self.__cancelling = True
        self._ok_cancelling_state = TaskStatus.finished
        self.__finish = True
        self.__state_lock.release()

    def is_cancelling(self):
        """return if communicator is cancelling (stoping, pusing, terminating)"""
        self.__state_lock.acquire()
        res = self.__cancelling
        self.__state_lock.release()
        return res

    def is_cancelled(self):
        """return if communicator is cancelled (stoping, pusing, terminating)"""
        self.__state_lock.acquire()
        res = self.__cancelled
        self.__state_lock.release()
        return res

    def terminate(self):
        """terminate communicator"""
        self.__state_lock.acquire()
        self.__terminate = True
        self.__cancelling = True
        self._ok_cancelling_state = TaskStatus.stopped
        self.__state_lock.release()

    def pause(self):
        """pause communicator"""
        self.__state_lock.acquire()
        self.__pause = True
        self.__cancelling = True
        self.__state_lock.release()
    
    def init_update(self):
        """get state and download all files"""
        self.__state_lock.acquire()
        self.__get_state = True
        self.__download = True
        self.__state_lock.release()        
        
    def run(self):
        while True:
            self.__state_lock.acquire()
            if self.__start:
                self.__start = False
                self.__state_lock.release()
                if not self._install():
                    break
                continue
            if self.__stop:
                self.__stop = False
                self.__state_lock.release()
                self._stop()                
                break
            if  self.__terminate:
                self.__terminate = False
                self.__state_lock.release()
                self._terminate()
                break
            if  self.__pause:
                self.__pause = False
                self.__state_lock.release()
                self._pause()
                break
            if self.__finish:
                self.__finish = False
                self.__state_lock.release()                
                self._results()
                self._state()
                self._stop()                
                break
            if self.__get_state:
                self.__get_state = False
                self.__state_lock.release()
                self._state()
                continue
            if self.__download:
                self.__download = False
                self.__state_lock.release()
                self._results()
                continue
            self.__state_lock.release() 
            time.sleep(0.1)
        self._com.close( )
        self.__state_lock.acquire()
        self.__cancelled = True
        self.__cancelling = False
        self.__state_lock.release()     
        
    def _install(self):
        """installation, if return False, thrad is stoped"""
        self._com.lock_installation()
        self._com.install()
        self._com. unlock_installation()
        if self._com.instalation_fails_mess is not None:
            self.__state_lock.acquire()
            self.__starting = False
            self.__error_state = True
            self.__error = self._com.instalation_fails_mess            
            self.__state_lock.release()
            return False            
        sec = time.time() + 1300
        message = tdata.Action(tdata.ActionType.installation).get_message()
        mess = None
        while sec > time.time():
            self._com.send_message(message)
            mess = self._com.receive_message(120)
            if mess is None:
                break
            if mess.action_type == tdata.ActionType.error:    
                if self._com.instalation_fails_mess is not None and \
                    mess.get_action().data.data["severity"]>4:
                    self.__state_lock.acquire()                    
                    self._ok_cancelling_state = TaskStatus.error
                    self.__start_state = TaskStatus.stopped
                    self.__error = mess.get_action().data.data["msg"]
                    self.__state_lock.release() 
                    self._stop()
                    self.__state_lock.acquire()
                    self.__starting = False
                    self.__state_lock.release()
                    return False
            if mess.action_type == tdata.ActionType.install_in_process:
                phase = mess.get_action().data.data['phase']
                self.__state_lock.acquire()
                self.__start_state = TaskStatus.installation
                if phase == TaskStatus.queued.value:
                    self.__start_state = TaskStatus.queued
                self.__state_lock.release()
            if mess.action_type == tdata.ActionType.ok:
                self.__state_lock.acquire()
                self.__starting = False
                self.__running = True
                self.__state_lock.release()
                return True                
            time.sleep(2)
        self.__state_lock.acquire()                    
        self._ok_cancelling_state = TaskStatus.error
        self.__start_state = TaskStatus.stopped
        self.__error = "Installation timeout exceed"
        self.__state_lock.release() 
        self._stop()
        self.__state_lock.acquire()
        self.__starting = False
        self.__state_lock.release()
        return False

    def _pause(self):
        """send pause mj action"""
        self._com.send_long_action(tdata.Action(
                    tdata.ActionType.interupt_connection))
        self._com.comunicator.interupt()
        self.__state_lock.acquire()
        state = self._last_state   
        state.status = TaskStatus.pause        
        self.__state = state
        self.__state_lock.release() 

    def _resume(self):
        """installation, if return False, thrad is stoped"""
        self._com.restore()
        self._com.send_long_action(tdata.Action(
            tdata.ActionType.restore_connection))
        self.__state_lock.acquire()
        self.__starting = False
        self.__running = True
        self.__state_lock.release()
 
    def _stop(self):
        mess = self._com.send_long_action(tdata.Action(
                    tdata.ActionType.stop))
        if mess is None or mess.action_type != tdata.ActionType.ok:
            action = tdata.Action( tdata.ActionType.destroy)
            message = action.get_message()
            self._com.send_message(message)
        self.__state_lock.acquire()
        state = self._last_state    
        if self._ok_cancelling_state is not None:
            if self._ok_cancelling_state==TaskStatus.error:
                self.__error_state = True
            state.status = self._ok_cancelling_state        
        self.__state = state
        self.__state_lock.release()        

    def _terminate(self):
        action = tdata.Action( tdata.ActionType.destroy)
        message = action.get_message()
        self._com.send_message(message)
        self.__state_lock.acquire()
        state = self._last_state    
        if self._ok_cancelling_state is not None:
            if self._ok_cancelling_state==TaskStatus.error:
                self.__error_state = True
            state.status = self._ok_cancelling_state        
        self.__state = state
        self.__state_lock.release()        
    
    def _state(self):
        mess = self._com.send_long_action(tdata.Action(
                    tdata.ActionType.get_state))
        if mess.action_type == tdata.ActionType.state:
            tmp_data = mess.get_action().data
            data = tmp_data.get_mjstate(self._com.mj_name)
            self.__state_lock.acquire()
            self.__state = data
            self.__state_lock.release()
 
    def _results(self):
        mess = self._com.send_long_action(tdata.Action(
                    tdata.ActionType.download_res))
        if mess.action_type == tdata.ActionType.ok:
            self._com.download()
            self.__state_lock.acquire()
            self.__downloaded = True
            self.__state_lock.release()

    @staticmethod
    def _set_loger(self,  path, name, level, central_log):
        """set logger"""
        logger = logging.getLogger("Remote")
        if len(logger.handlers)>0:
            if logger.level>level:
                logger.setLevel(level)
                logger.handlers[0].setLevel(level)
            return
        dir = os.path.join(__install_dir__, "log")
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except:
                dir = __install_dir__
        log_file = os.path.join(dir, "app-centrall.log")
        logger.setLevel(level)

        fh = logging.FileHandler(log_file)
        fh.setLevel(level)

        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s')

        fh.setFormatter(formatter)
        logger.addHandler(fh)    
        logger.debug("ComManager is started")
        
    @staticmethod
    def get_loger():
        """get logger"""
        return logging.getLogger("Remote")
