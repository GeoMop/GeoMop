# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
import os

logger = logging.getLogger("UiTrace")
import threading
import data.transport_data as tdata
import communication.installation as inst


class DataReloader(threading.Thread):

    def __init__(self, data=None):
        super(DataReloader, self).__init__()
        self._data = data
        self._isRunning = False
        self._communicators = list()

    def run(self):
        self._isRunning = True
        while self._isRunning:
            for idx, communicator in enumerate(self._communicators):
                mess = communicator["communicator"].send_long_action(
                    tdata.Action(tdata.ActionType.download_res))
                communicator["communicator"].download()
                self._data_received(communicator)
                logger.debug("Downloading data from communicator with "
                             "message: %s", mess)

        logger.debug("App is shutting Down.")
        for communicator in self._communicators:
            mess = communicator["communicator"].send_long_action(
                tdata.Action(tdata.ActionType.stop))
            logger.debug("Closing communicator with response: %s", mess)
            communicator["communicator"].close()

    def stop(self):
        self._isRunning = False

    def install_communicator(self, key, communicator):
        communicator.install()
        communicator.send_long_action(
            tdata.Action(tdata.ActionType.installation))
        self._communicators.append({"key": key, "communicator": communicator})

    def _data_received(self, communicator):
        res_path = inst.Installation.get_result_dir_static(
            communicator["communicator"].mj_name)
        logs = [os.path.join(res_path, f) for f in os.listdir(res_path)]
        for log in logs:
            log = res_path + log
        self._data.multijobs[communicator["key"]]["logs"] = logs
        self.notify_data_changed(communicator["key"])

    def message_received(self, idx, mess):
        pass

    def notify_data_changed(self, key):
        pass
