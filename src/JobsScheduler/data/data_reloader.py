# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import threading
from enum import IntEnum
from queue import Queue

import data.transport_data as tdata


class DataReloader(threading.Thread):
    def __init__(self):
        super().__init__()
        self.req_queue = Queue(50)
        self.res_queue = Queue(50)
        self.coms = dict()
        self._is_running = threading.Event()

    def run(self):
        self._is_running.set()
        # main loop
        while self._is_running.is_set():
            while not self.req_queue.empty():
                print("God Request")
                req = self.req_queue.get()
                worker = CommunicationWorker(
                    req.key, self.coms[req.key], req.com_type, self.res_queue)
                worker.start()
        # exit procedures
        print("Exiting")
        for key in self.coms:
            worker = CommunicationWorker(
                key, self.coms[key], CommunicationType.stop, self.res_queue)
            worker.start()

    def stop(self):
        self._is_running.clear()


class CommunicationType(IntEnum):
        """Type of desired communication action"""
        install = 0
        results = 1
        state = 2
        interrupt = 2
        stop = 3


class ReqData(object):
    def __init__(self, key, com_type):
        self.key = key
        self.com_type = com_type


class ResData(object):
    def __init__(self, key, com_type, res=None):
        self.key = key
        self.com_type = com_type
        self.res = res


class CommunicationWorker(threading.Thread):
    def __init__(self, key, com, com_type, res_queue):
        self.key = key
        self.com = com
        self.com_type = com_type
        self.res_queue = res_queue
        self.res = None
        super().__init__(name=com.mj_name)

    def run(self):
        print("Communicating")
        # install
        if self.com_type == CommunicationType.install:
            self.com.install()
            self.res = self.com.send_long_action(tdata.Action(
                tdata.ActionType.installation))

        # download results
        elif self.com_type == CommunicationType.results:
            self.res = self.com.send_long_action(tdata.Action(
                tdata.ActionType.download_res))
            self.com.download()

        # stop
        elif self.com_type == CommunicationType.stop:
            self.res = self.com.send_long_action(tdata.Action(
                tdata.ActionType.stop))
            self.com.close()

        # insert into res queue
        print("Got response")
        self.res_queue.put(ResData(self.key, self.com_type, self.res))

