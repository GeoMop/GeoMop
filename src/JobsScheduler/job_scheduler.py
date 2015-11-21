#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start script that initializes main window and runs APP
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os
import sys
import logging
import PyQt5.QtWidgets as QtWidgets

# import common directory to path (should be in __init__)
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)
sys.path.insert(2, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(3, './twoparty/enum')

from ui.com_manager import ComManager, ComManagerMock
from ui.main_window import MainWindow
from ui.data.data_structures import DataContainer

# logging setup on STDOUT or to FILE
logger = logging.getLogger("UiTrace")

logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s|%(levelname)s: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class JobsScheduler(object):
    """Jobs Scheduler main class"""

    def __init__(self, args):
        """Initialization of UI with executive code"""
        # setup qt app
        self._app = QtWidgets.QApplication(args)

        # load data container
        self._data = DataContainer()

        # setup com manager
        self._com_manager = ComManager()

        # setup qt UI
        self._main_window = MainWindow(data=self._data,
                                       com_manager=self._com_manager)

        # connect reloader kill on app exit
        self._app.aboutToQuit.connect(
            self._main_window.handle_terminate)

        # connect save all on exit
        self._app.aboutToQuit.connect(self._data.save_all)

    def run(self):
        """Run app and show UI"""

        # show UI
        self._main_window.show()

        # execute app
        sys.exit(self._app.exec_())

if __name__ == "__main__":
    # init and run APP
    APP = JobsScheduler(sys.argv)
    APP.run()
