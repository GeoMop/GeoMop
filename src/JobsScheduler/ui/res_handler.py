# -*- coding: utf-8 -*-
"""
Timer that gets data from threads and notifies main window to refresh view
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from ui.com_manager import ComType


class ResHandler(QTimer):
    mj_stoped = QtCore.pyqtSignal(str)
    mj_installed = QtCore.pyqtSignal(str)
    mj_result = QtCore.pyqtSignal(str, dict)
    mj_state = QtCore.pyqtSignal(str, object)

    def __init__(self, com_manager, parent=None):
        super().__init__(parent)
        self.com_manager = com_manager
        # connect handle slot
        self.timeout.connect(self._handle_timeout)
        self.start(2)

    def _handle_timeout(self):
        while not self.com_manager.res_queue.empty():
                res = self.com_manager.res_queue.get()
                if res.com_type is ComType.install:
                    self.mj_installed.emit(res.key)
                elif res.com_type is ComType.stop:
                    self.mj_stoped.emit(res.key)
                elif res.com_type is ComType.results:
                    self.mj_result.emit(res.key, res.data)
                elif res.com_type is ComType.state:
                    self.mj_state.emit(res.key, res.data)
