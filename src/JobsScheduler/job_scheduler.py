#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start script that initializes main window and runs APP
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import sys
import os
import logging

import PyQt5.QtWidgets as QtWidgets
from ui.main_window import MainWindow
from data.data_structures import DataContainer


class JobsScheduler(object):
    """Jobs Scheduler main class"""

    def __init__(self, args):
        """Initialization of UI with executive code"""
        # log app init
        logging.info('==== %s initialization ====', self.__class__.__name__)

        # setup qt app
        self._app = QtWidgets.QApplication(args)

        # load data container
        self._data = DataContainer()

        # setup qt UI
        self._main_window = MainWindow(data=self._data)

    def run(self):
        """Run app and show UI"""

        # show UI
        self._main_window.show()

        # log app start
        logging.info('==== %s is running  ====', self.__class__.__name__)

        # execute app
        sys.exit(self._app.exec_())

if __name__ == "__main__":
    # import common directory to path (should be in __init__)
    sys.path.append(".." + os.pathsep + "common")

    # logging setup on STDOUT or to FILE
    logging.basicConfig(  # filename='jobscheduler.log',
                          stream=sys.stdout,
                          datefmt='%d.%m.%Y|%H:%M:%S',
                          format='%(asctime)s|%(levelname)s: %(message)s',
                          level=logging.DEBUG)

    # init and run APP
    APP = JobsScheduler(sys.argv)
    APP.run()
