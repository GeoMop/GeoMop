import threading
import time
from queue import Empty
import logging
import os
import data.transport_data as tdata
from multiprocessing import Queue
from data.states import TaskStatus
from  communication.installation import __install_dir__

class ComWorker(threading.Thread):
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

    def __init__(self, key, com):            
        super().__init__(name=com.mj_name)
        self._error = None
        """if returned state is error, this variable contain error message"""
        
        self.is_stopping = False
        
        self.key = key
        self.com = com
        self.is_ready = threading.Event()
        self._is_running = threading.Event()
        self.req_queue = Queue()
        self.res_queue = res_queue
        self.start()
        
    def get_last_results(self, is_current):
        """
        return tupple (state, error, jobs_downloaded, results_downloaded , logs_downloaded)
        if new state is not known return None
        if new files is not downloaded return None
        
        parameters:
        :param bool is_current: is job selected in gui
        """
    
    def start(self):
        """start communication"""
        
    def resume(self):
        """resume communication"""
        
    def is_started(self):
        """return if communication is started"""
        
    def is_interupted(self):
        """return if communication is interupted"""
        
    def is_error(self):
        """return if communication is interupted"""
        
    def stop(self):
        """stop communicator"""

    def is_stopping(self):
        """return if communicator is stopping"""

    def is_stopped(self):
        """return if communicator is stopped"""

    def terminate(self):
        """terminate if communicator"""

    def is_terminating(self):
        """return if communicator is terminating"""

    def is_terminated(self):
        """return if communicator is terminated"""
        
    def init_update(self):
        """get state and download all files"""
        
    def get_error(self):
        """get state and download all files"""


    def drop_all_req(self):
        while not self.req_queue.empty():
            try:
                self.req_queue.get(False, 0)
            except Empty:
                continue

    def run(self):
        error = None
        self.is_ready.set()
        self._is_running.set()
        while self._is_running.is_set():
            req = self.req_queue.get()
            res = ComExecutor.communicate(self.com, req,
                                            self.res_queue)
            if res.err is not None:
                if self.com.output is None or not self.com.output.isconnected():
                    res.com_type=ComType.stop
                self._is_running.clear()                     
                break
            else:
                self.res_queue.put(res)
            if req.com_type == ComType.stop:
                self._is_running.clear() 
                break
        if self.com.output is not None and self.com.output.isconnected() and \
            req.com_type != ComType.stop:
            error = res.err
            res = ComExecutor.communicate(
                self.com, ReqData(self.key, ComType.stop), self.res_queue)
            res.err = error
        self.com.close()
        self.res_queue.put(res)

    def stop(self):
        self._is_running.clear()

    def is_stopped(self):
        return not self._is_running.is_set()


class ComExecutor(object):
    @classmethod
    def communicate(cls, com, req, res_queue):
        res = ResData(req.key, req.com_type)
        try:
            # install
            if req.com_type == ComType.install:
                res = cls._install(com, res, res_queue)

            # download results
            elif req.com_type == ComType.results:
                res = cls._results(com, res)

            # pause results
            elif req.com_type == ComType.pause:
                res = cls._pause(com, res)

            # resume results
            elif req.com_type == ComType.resume:
                res = cls._resume(com, res)

            # stop
            elif req.com_type == ComType.stop:
                res = cls._stop(com, res)

            # state
            elif req.com_type == ComType.state:
                res = cls._state(com, res)

            else:
                raise Exception("Unsupported operation.")

        except Exception as e:
            res.err = e

        return res

    @staticmethod
    def _install(com, res, res_queue):
        old_phase = TaskStatus.installation
        com.install()
        if com.instalation_fails_mess is not None:
            raise Exception(com.instalation_fails_mess)    
        sec = time.time() + 1300
        message = tdata.Action(tdata.ActionType.installation).get_message()
        mess = None
        while sec > time.time():
            com.send_message(message)
            mess = com.receive_message(120)
            if mess is None:
                break
            if mess.action_type == tdata.ActionType.error:    
                if com.instalation_fails_mess is not None and \
                    mess.get_action().data.data["severity"]>4:
                    raise Exception(mess.get_action().data.data["msg"])    
            if mess.action_type == tdata.ActionType.install_in_process:
                phase = mess.get_action().data.data['phase']
                if phase is not old_phase:
                    if phase == TaskStatus.installation.value:
                        res_queue.put(
                                ResData(res.key, ComType.installation, mess))
                    if phase == TaskStatus.queued.value:
                        res_queue.put(ResData(res.key, ComType.queued, mess))
            else:
                break
            time.sleep(2)
            res.mess = mess
        return res

    @staticmethod
    def _pause(com, res):
        res.mess = com.send_long_action(tdata.Action(
            tdata.ActionType.interupt_connection))
        com.interupt()
        return res

    @staticmethod
    def _resume(com, res):
        com.restore()
        res.mess = com.send_long_action(tdata.Action(
            tdata.ActionType.restore_connection))
        return res

    @staticmethod
    def _stop(com, res):
        res.mess = com.send_long_action(tdata.Action(
                    tdata.ActionType.stop))        
        return res

    @staticmethod
    def _state(com, res):
        res.mess = com.send_long_action(tdata.Action(
                    tdata.ActionType.get_state))
        if res.mess.action_type == tdata.ActionType.state:
            tmp_data = res.mess.get_action().data
            res.data = tmp_data.get_mjstate(com.mj_name)
        return res

    @staticmethod
    def _results(com, res):
        res.mess = com.send_long_action(tdata.Action(
                    tdata.ActionType.download_res))
        com.download()
        return res
