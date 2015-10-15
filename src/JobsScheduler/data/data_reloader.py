# -*- coding: utf-8 -*-
"""
JobScheduler data reloader
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
from threading import Thread
from time import sleep


class DataReloader(Thread):
    _isRunning = False
    data = None

    def __init__(self, data=None):
        super(DataReloader, self).__init__()
        self.data = data

    def run(self):
        self._isRunning = True
        while self._isRunning:
            sleep(1)
            logging.info('%s is running...', self.__class__.__name__)

    def stop(self):
        self._isRunning = False
