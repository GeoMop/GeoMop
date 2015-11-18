# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os
import threading
import data.transport_data as tdata
from enum import IntEnum
from multiprocessing import Queue

from communication import Installation
from data.states import JobsState, TaskStatus


class ComManager(object):
    def __init__(self):
        self.res_queue = Queue()
        self._workers = dict()

    def install(self, key, com):
        worker = ComWorker(key=key, com=com, res_queue=self.res_queue)
        req = ReqData(key=key, com_type=ComType.install)
        worker.req_queue.put(req)
        self._workers[worker.key] = worker

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
        worker.req_queue.put(req)

    def is_installed(self, key):
        if self._workers.get(key, None):
            return True
        else:
            return False

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
        interrupt = 2
        stop = 3


class ComWorker(threading.Thread):
        def __init__(self, key, com, res_queue):
            self.key = key
            self.com = com
            self.req_queue = Queue()
            self.res_queue = res_queue
            super().__init__(name=com.mj_name)
            self.start()

        def run(self):
            while True:
                req = self.req_queue.get()
                print("Got Req")
                if req is None:
                    break
                else:
                    res = ComExecutor.communicate(self.com, req)
                    self.res_queue.put(res)
                    print("Got Res")
            res = ComExecutor.communicate(
                self.com, ReqData(self.key, ComType.stop))
            self.res_queue.put(res)

        def stop(self):
            self.req_queue.put(None)


class ComExecutor(object):
    @classmethod
    def communicate(cls, com, req):
        res = ResData(req.key, req.com_type)
        try:
            # install
            if req.com_type == ComType.install:
                res = cls._install(com, res)
            # download results
            elif req.com_type == ComType.results:
                res = cls._results(com, res)

            # stop
            elif req.com_type == ComType.stop:
                res = cls._stop(com, res)

            # state
            elif req.com_type == ComType.state:
                res = cls._state(com, res)

        except Exception as e:
            res.err = e

        return res

    @staticmethod
    def _install(com, res):
        com.install()
        res.mess = com.send_long_action(tdata.Action(
            tdata.ActionType.installation))
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
            res.data = tmp_data.get_mjstate(com.mj_name).__dict__
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
            "conf": conf_path
        }
        return res


class MockComExecutor(ComExecutor):
    @staticmethod
    def _install(com, res):
        res.mess = "OK - Installed"
        return res

    @staticmethod
    def _state(com, res):
        res.mess = "OK - State"
        res.data = {
            'qued_time': 1447672171.6055062,
            'start_time': 1447672151.6055062,
            'run_interval': 50,
            'status': TaskStatus.running.name,
            'insert_time': 1447672161.6055062,
            'running_jobs': 2,
            'finished_jobs': 0,
            'name': 'testmj',
            'estimated_jobs': 2,
            'known_jobs': 2}
        return res

    @staticmethod
    def _stop(com, res):
        res.mess = "OK - Stop"
        return res

    @staticmethod
    def _results(com, res):
        res_path = Installation.get_result_dir_static(com.mj_name)
        log_path = os.path.join(res_path, "log")
        conf_path = Installation.get_config_dir_static(com.mj_name)
        states = JobsState()
        states.load_file(res_path)
        res.data = {
            "jobs": states.jobs,
            "logs": log_path,
            "conf": conf_path
        }
        return res
