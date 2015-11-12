# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
import os
import threading
import time

import communication.installation as inst
import data.transport_data as tdata

logger = logging.getLogger("UiTrace")


class DataReloader(threading.Thread):
    def __init__(self):
        super(DataReloader, self).__init__()
        self._to_install = list()
        self._communicators = list()
        self.results = dict()
        self._is_running = threading.Event()
        self.needs_reload = threading.Event()
        self.main_key = None

    def run(self):
        self._is_running.set()
        while self._is_running.is_set():
            # install new coms
            install_pool = CommunicatorPool()
            for com in self._to_install:
                comworker = CommunicatorWorker(com["key"],
                                               com["communicator"],
                                               tdata.ActionType.installation)
                install_pool.coms.append(comworker)
            install_pool.start_all()
            results = install_pool.wait_for_results()
            for idx, result in enumerate(results):
                self._to_install[idx]["messages"].append(result)
                self._communicators.append(self._to_install.pop(idx))

            if self.needs_reload.is_set():
                # download data
                for idx, com in enumerate(self._communicators):
                    mess = com["communicator"].send_long_action(
                        tdata.Action(tdata.ActionType.download_res))
                    com["communicator"].download()
                    com["messages"].append(mess)
                    self._prepare_results(com)
                    logger.debug("Downloading data from communicator with "
                                 "message: %s", mess)
                self.needs_reload.clear()
            else:
                time.sleep(1)

        # stop communication on exit
        logger.debug("Reloader is shutting Down.")
        for idx, com in enumerate(self._communicators):
            mess = com["communicator"].send_long_action(
                tdata.Action(tdata.ActionType.stop))
            com["communicator"].close()
            com["messages"].append(mess)

    def stop(self):
        self._is_running.clear()

    def install_communicator(self, key, communicator):
        com_entry = {
            "key": key,
            "communicator": communicator,
            "messages": list()
        }
        self._to_install.append(com_entry)
        self.needs_reload.set()

    def _prepare_results(self, com):
        res_path = inst.Installation.get_result_dir_static(
            com["communicator"].mj_name)
        conf_path = inst.Installation.get_config_dir_static(
            com["communicator"].mj_name)
        log_path = os.path.join(res_path, "log")
        self.results[com["key"]] = dict()
        self.results[com["key"]]["logs"] = log_path
        self.results[com["key"]]["conf"] = conf_path
        self.results[com["key"]]["messages"] = com["messages"]


class CommunicatorWorker(threading.Thread):
    def __init__(self, key, com, action_type, res=None):
        self.key = key
        self.com = com
        self.action_type = action_type
        self.res = res
        super().__init__(name=com.mj_name)

    def run(self):
        # Install
        if self.action_type == tdata.ActionType.installation:
            self.com.install()
            self.res = self.com.send_long_action(tdata.Action(
                tdata.ActionType.installation))

        # Download
        elif self.action_type == tdata.ActionType.download_res:
            self.res = self.com.send_long_action(tdata.Action(
                tdata.ActionType.download_res))
            self.com.download()

        # Stop
        elif self.action_type == tdata.ActionType.stop:
            self.res = self.com.send_long_action(tdata.Action(
                tdata.ActionType.stop))
            self.com.close()


class CommunicatorPool(object):
    def __init__(self):
        super().__init__()
        self.coms = list()

    def start_all(self):
        for com in self.coms:
            com.start()

    def start_one_by_one(self):
        for com in self.coms:
            com.start()
            com.join()

    def wait_for_results(self):
        results = list()
        for com in self.coms:
            com.join()
            results.append(com.res)
        return results
