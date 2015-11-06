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

    def run(self):
        self._is_running.set()
        while self._is_running.is_set():
            # install new coms
            for idx, com in enumerate(self._to_install):
                com["communicator"].install()
                mess = com["communicator"].send_long_action(
                    tdata.Action(tdata.ActionType.installation))
                com["messages"].append(mess)
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
        res_path = inst.Installation \
            .get_result_dir_static(com["communicator"].mj_name)
        logs = [os.path.join(res_path, f) for f in os.listdir(res_path)][1:]
        for log in logs:
            log = res_path + log
        self.results[com["key"]] = dict()
        self.results[com["key"]]["logs"] = logs
