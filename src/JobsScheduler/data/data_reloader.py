# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging

logger = logging.getLogger("UiTrace")
from threading import Thread
from time import sleep


class DataReloader(Thread):

    def __init__(self, data=None):
        super(DataReloader, self).__init__()
        self.data = data
        self._isRunning = False
        self.communicators = list()

    def run(self):
        self._isRunning = True
        while self._isRunning:
            sleep(1)
            logger.info('%s is running...', self.__class__.__name__)

    def stop(self):
        self._isRunning = False

        # def add_communicator