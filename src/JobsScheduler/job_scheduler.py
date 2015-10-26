#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start script that initializes main window and runs APP
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os
import sys
# import common directory to path (should be in __init__)
# sys.path.append(".." + os.pathsep + "common")
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

import logging
# logging setup on STDOUT or to FILE
logging.basicConfig(  # filename='jobscheduler.log',
                      stream=sys.stdout,
                      datefmt='%d.%m.%Y|%H:%M:%S',
                      format='%(asctime)s|%(levelname)s: %(message)s',
                      level=logging.DEBUG)
import PyQt5.QtWidgets as QtWidgets

from data.data_reloader import DataReloader
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

        # load data reloader
        self._reloader = DataReloader(self._data)

        # setup qt UI
        self._main_window = MainWindow(data=self._data)

        # connect reloader kill on app exit
        self._app.aboutToQuit.connect(self._reloader.stop)

        # connect save all on exit
        self._app.aboutToQuit.connect(self._data.save_all)

    def run(self):
        """Run app and show UI"""
        # start data reloader
        self._reloader.start()

        # show UI
        self._main_window.show()

        # log app start
        logging.info('==== %s is running  ====', self.__class__.__name__)

        # execute app
        sys.exit(self._app.exec_())

if __name__ == "__main__":
    # init and run APP
    APP = JobsScheduler(sys.argv)
    APP.run()
