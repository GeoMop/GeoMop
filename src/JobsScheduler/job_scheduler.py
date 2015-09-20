#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start script that initializes main window
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

# import common directory to path
import sys
import os
# sys.path.append("../common")

__lib_dir__ = os.path.join(
    os.path.split(
        os.path.dirname(
            os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

import PyQt5.QtWidgets as QtWidgets
from ui.main_window import MainWindow
from data.data_structures import DataContainer
import logging


class JobsScheduler(object):
    """Jobs Scheduler main class"""

    def __init__(self):
        """Initialization of UI with executive code"""
        # logging setup on STDOUT or to FILE
        logging.basicConfig(#filename='jobscheduler.log',
                            stream=sys.stdout,
                            datefmt='%d.%m.%Y|%H:%M:%S',
                            format='%(asctime)s|%(levelname)s: %(message)s',
                            level=logging.DEBUG)
        logging.info('==== %s started ====', self.__class__.__name__)
        # qt app setup
        self._app = QtWidgets.QApplication(sys.argv)
        # data container with config handler inserted
        self._data = DataContainer()
        # qt UI
        self._main_window = MainWindow(data=self._data)
        logging.info('==== %s drawn ====',
                     self._main_window.__class__.__name__)
        # show UI
        self._main_window.show()
        logging.info('==== %s shown ====',
                     self._main_window.__class__.__name__)
        sys.exit(self._app.exec_())

if __name__ == "__main__":
    APP = JobsScheduler()
