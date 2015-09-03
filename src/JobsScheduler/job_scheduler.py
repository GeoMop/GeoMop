#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start script that initializes main window
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import os
import sys
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "lib")
sys.path.insert(1, __lib_dir__)

import PyQt5.QtWidgets as QtWidgets
from ui.main_window import MainWindow
from ui.dialogs.multijob import MultiJobDialog
from ui.dialogs.ssh_presets import SshPresets


class JobsScheduler(object):
    """Jobs Scheduler main class"""

    def __init__(self):
        """Initialization of UI"""
        self._app = QtWidgets.QApplication(sys.argv)
        self._main_window = MainWindow()
        self._main_window.show()
        sys.exit(self._app.exec_())

if __name__ == "__main__":
    APP = JobsScheduler()
