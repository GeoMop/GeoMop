# -*- coding: utf-8 -*-
"""
Timer that gets data from threads and notifies main window to refresh view
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from data.data_reloader import CommunicationType


class WindowRefresher(QTimer):
    mj_stoped = QtCore.pyqtSignal(str)
    mj_installed = QtCore.pyqtSignal(str)

    def __init__(self, data_reloader, parent=None):
        super().__init__(parent)
        self.data_reloader = data_reloader
        # connect handle slot
        self.timeout.connect(self._handle_timeout)

    def _handle_timeout(self):
        while not self.data_reloader.res_queue.empty():
                res = self.data_reloader.res_queue.get()
                if res.com_type is CommunicationType.install:
                    self.mj_installed.emit(res.key)
