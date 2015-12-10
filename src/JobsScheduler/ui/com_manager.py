# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os
import threading
import time
from queue import Empty

import data.transport_data as tdata
from enum import IntEnum
from multiprocessing import Queue

from communication import Installation
from data.states import JobsState, MJState, TaskStatus


class ComManager:
    def __init__(self):
        self.res_queue = Queue()
        self._workers = dict()

    def install(self, key, com):
        worker = ComWorker(key=key, com=com, res_queue=self.res_queue)
        req = ReqData(key=key, com_type=ComType.install)
        worker.req_queue.put(req)
        self._workers[worker.key] = worker

    def pause(self, key):
        worker = self._workers[key]
        worker.is_ready.clear()
        req = ReqData(key=key, com_type=ComType.pause)
        worker.drop_all_req()
        worker.req_queue.put(req)

    def resume(self, key):
        worker = self._workers[key]
        worker.is_ready.set()
        req = ReqData(key=key, com_type=ComType.resume)
        worker.req_queue.put(req)

    def restart(self, key):
        worker = self._workers[key]
        req_stop = ReqData(key=key, com_type=ComType.pause)
        req_run = ReqData(key=key, com_type=ComType.resume)
        worker.req_queue.put(req_stop)
        worker.req_queue.put(req_run)

    def state(self, key):
        worker = self._workers[key]
        req = ReqData(key=key, com_type=ComType.state)
        worker.req_queue.put(req)

    def results(self, key):
        worker = self._workers[key]
        req = ReqData(key=key, com_type=ComType.results)
        worker.req_queue.put(req)

    def stop(self, key):
        worker = self._workers[key]
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

    def terminate(self):
        for key in self._workers:
            self._workers[key].stop()


class ComManagerMock:
    def __init__(self):
        self.res_queue = Queue()
        self._workers = dict()
        self._last_state = dict()

    def install(self, key, com):
        self._workers[key] = com
        mess = tdata.Message()
        res = ResData(key, ComType.install, mess)
        self.res_queue.put(res)
        self._last_state[key] = True

    def pause(self, key):
        mess = tdata.Message()
        res = ResData(key, ComType.pause, mess)
        self.res_queue.put(res)
        self._last_state[key] = False

    def resume(self, key):
        mess = tdata.Message()
        res = ResData(key, ComType.resume, mess)
        self.res_queue.put(res)
        self._last_state[key] = True

    def restart(self, key):
        mess = tdata.Message()
        res_pause = ResData(key, ComType.pause, mess)
        self.res_queue.put(res_pause)
        res_resume = ResData(key, ComType.resume, mess)
        self.res_queue.put(res_resume)
        self._last_state[key] = True

    def state(self, key):
        mess = tdata.Message()
        data = MJState(self._workers[key].mj_name)
        data.insert_time = 1448021814
        data.qued_time = 1448021814
        data.start_time = 1448021814
        data.run_interval = 20
        data.status = TaskStatus.running
        data.known_jobs = 35
        data.estimated_jobs = 10
        data.finished_jobs = 20
        data.running_jobs = 5
        res = ResData(key, ComType.state, mess, None, data)
        self.res_queue.put(res)

    def results(self, key):
        mess = tdata.Message()
        job1 = JobsState()
        job1.name = "testjob1"
        job1.insert_time = 1448021814
        job1.qued_time = 1448021814
        job1.start_time = 1448021814
        job1.run_interval = 0
        job1.status = TaskStatus.running

        job2 = JobsState()
        job2.name = "testjob1"
        job2.insert_time = 1448021814
        job2.qued_time = 1448021814
        job2.start_time = 1448021814
        job2.run_interval = 0
        job2.status = TaskStatus.running
        res_path = Installation.get_result_dir_static(
            self._workers[key].mj_name)
        log_path = os.path.join(res_path, "log")
        conf_path = Installation.get_config_dir_static(
            self._workers[key].mj_name)
        data = {
            "jobs": [job1, job2],
            "logs": log_path,
            "conf": conf_path
        }
        res = ResData(key, ComType.results, mess, None, data)
        self.res_queue.put(res)

    def stop(self, key):
        mess = tdata.Message()
        del self._workers[key]
        res = ResData(key, ComType.stop, mess)
        self.res_queue.put(res)
        self._last_state[key] = False

    def is_installed(self, key):
        if self._workers.get(key, None):
            return self._last_state.get(key, False)
        else:
            return False

    def is_busy(self, key):
        if self.res_queue.empty():
            return False
        return True

    def terminate(self):
        pass


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
        qued = 6


class ComWorker(threading.Thread):
        def __init__(self, key, com, res_queue):
            super().__init__(name=com.mj_name)
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
            self.is_ready.set()
            self._is_running.set()
            while self._is_running.is_set():
                req = self.req_queue.get()
                if req is None:
                    break
                else:
                    res = ComExecutor.communicate(self.com, req,
                                                  self.res_queue)
                    self.res_queue.put(res)
            res = ComExecutor.communicate(
                self.com, ReqData(self.key, ComType.stop), self.res_queue)
            self.res_queue.put(res)

        def stop(self):
            self._is_running.clear()
            self.req_queue.put(None)


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
        sec = time.time() + 600
        message = tdata.Action(tdata.ActionType.installation).get_message()
        mess = None
        while sec > time.time():
            com.send_message(message)
            mess = com.receive_message(120)
            if mess is None:
                break
            if mess.action_type == tdata.ActionType.install_in_process:
                phase = mess.get_action().data.data['phase']
                if phase is not old_phase:
                    # add to queue
                    res_queue.put(ResData(res.key, ComType.qued, mess))
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
        com.close()
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
        res_path = Installation.get_result_dir_static(com.mj_name)
        log_path = os.path.join(res_path, "log")
        conf_path = Installation.get_config_dir_static(com.mj_name)
        states = JobsState()
        states.load_file(res_path)
        res.data = {
            "jobs": states.jobs,
            "logs": log_path,
            "conf": conf_path,
            "res": res_path
        }
        return res
