# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import threading
import time
from queue import Empty

import data.transport_data as tdata
from enum import IntEnum
from multiprocessing import Queue
from data.states import TaskStatus

class ComManager:
    """
    Usage:
    
        - set application data to constructor
        - add job id (key) to array (start_jobs,stop_jobs,resume_jobs)
        - if current job is changed, set it
        - each 1s call check function in main thread, after check returning should be done:    
        
                -  from arrays state_change_jobs,results_change_jobs,jobs_change_jobs pull
                    jobs, and fix graphic presentation

        - call stop or resume function and wait till run_jobs and start_jobs array is not empty
    """
    def __init__(self, data_app):        
        self.res_queue = Queue()
        self._workers = dict()
        self._data_app = data_app
        self.current_job = None
        """current job id"""
        self.start_jobs = []
        """array of job ids, that will be started"""
        self.resume_jobs = []
        """array of jobs ids, that will be resume"""
        self.stop_jobs = []
        """array of jobs ids, that will be stopped"""
        self.run_jobs = []
        """array of running jobs ids"""
        self.state_change_jobs=[]
        """array of jobs ids, that have changed state"""
        self.results_change_jobs=[]
        """array of jobs ids, that have changed results"""
        self.jobs_change_jobs=[]
        """array of jobs ids, that have changed jobs state"""
        
    def check(self):
        """
        This function plan and make all needed action in main thread.
        Call this function in some period
        """
        
    def resume_all(self):
        """resume all running and starting jobs"""
        
    def stop(self):
        """stop all running and starting jobs"""
        
    # next funcion will be delete after refactoring

    def create_worker(self, key, com):        
        worker = ComWorker(key=key, com=com, res_queue=self.res_queue)
        self._workers[worker.key] = worker

    def install(self, key, com):
        worker = ComWorker(key=key, com=com, res_queue=self.res_queue)
        req_install = ReqData(key=key, com_type=ComType.install)
        req_results = ReqData(key=key, com_type=ComType.results)
        worker.req_queue.put(req_install)
        worker.req_queue.put(req_results)
        self._workers[worker.key] = worker

    def pause(self, key):
        if key in self._workers:
            worker = self._workers[key]        
            worker.is_ready.clear()
            req = ReqData(key=key, com_type=ComType.pause)
            worker.drop_all_req()
            worker.req_queue.put(req)

    def resume(self, key):
        if key in self._workers:
            worker = self._workers[key]
            worker.is_ready.set()
            req = ReqData(key=key, com_type=ComType.resume)
            worker.req_queue.put(req)

    def state(self, key):
        if key in self._workers:
            worker = self._workers[key]
            if worker.is_stopping:
                return
            req = ReqData(key=key, com_type=ComType.state)
            worker.req_queue.put(req)

    def results(self, key):
        if key in self._workers:
            worker = self._workers[key]
            if worker.is_stopping:
                return
            req = ReqData(key=key, com_type=ComType.results)
            worker.req_queue.put(req)

    def finish(self, key):
        if key in self._workers:
            worker = self._workers[key]
            worker.is_stopping = True
            req_result = ReqData(key=key, com_type=ComType.results)
            req_stop = ReqData(key=key, com_type=ComType.stop)
            worker.req_queue.put(req_result)
            worker.req_queue.put(req_stop)

    def stop(self, key):
        if key in self._workers:
            worker = self._workers[key]
            worker.is_stopping = True
            worker.is_ready.clear()
            req = ReqData(key=key, com_type=ComType.stop)
            worker.drop_all_req()
            worker.req_queue.put(req)

    def is_installed(self, key):
        if self._workers.get(key, None):
            return True
        else:
            return False

    def is_busy(self, key):
        worker = self._workers.get(key, None)
        if worker.req_queue.empty() and worker.is_ready.is_set():
            return False
        return True
        
    def get_communicator(self, key):
        return self._workers[key].com
        
    def check_workers(self):
        """Check processis, end terminate finished"""
        for key, worker in self._workers.items():
            if worker.is_stopped():
                del self._workers[key]
                return key
        return None

    def terminate(self):
        for key in self._workers:
            self._workers[key].stop()


class ReqData(object):
    def __init__(self, key, com_type, data=None):
        self.key = key
        self.com_type = com_type
        self.data = data


class ResData(object):
    def __init__(self, key, com_type, mess=None, err=None, data=None):
        self.key = key
        self.com_type = com_type
        self.mess = mess
        self.err = err
        self.data = data


class ComType(IntEnum):
        """Type of desired communication action"""
        install = 0
        results = 1
        state = 2
        pause = 3
        resume = 4
        stop = 5
        queued = 6
        installation = 7


class ComWorker(threading.Thread):
        def __init__(self, key, com, res_queue):            
            super().__init__(name=com.mj_name)
            self.is_stopping = False
            self.key = key
            self.com = com
            self.is_ready = threading.Event()
            self._is_running = threading.Event()
            self.req_queue = Queue()
            self.res_queue = res_queue
            self.start()

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
            time.sleep(10)
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
