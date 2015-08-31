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

import os
import PyQt5.QtWidgets as QtWidgets
from panels.main_window import UiMainWindow
from dialogs.add_multijob import AddMultiJobDialog


class JobsScheduler(object):
    """Jobs Scheduler main class"""

    def __init__(self):
        """Initialization of UI"""
        self._app = QtWidgets.QApplication(sys.argv)
        self._ui = UiMainWindow()

        # test action
        self._ui.menu_exit_action.triggered.connect(QtWidgets.qApp.quit)
        self._add_multijob_dlg = AddMultiJobDialog()
        #print(self._ui.findChild(QtWidgets.QWidget, "tableView"))
        sys.exit(self._app.exec_())

if __name__ == "__main__":
    APP = JobsScheduler()
