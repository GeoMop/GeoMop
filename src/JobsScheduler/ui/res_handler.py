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
    mj_installed = QtCore.pyqtSignal(str)
    mj_qued = QtCore.pyqtSignal(str)
    mj_paused = QtCore.pyqtSignal(str)
    mj_resumed = QtCore.pyqtSignal(str)
    mj_stopped = QtCore.pyqtSignal(str)
    mj_result = QtCore.pyqtSignal(str, dict)
    mj_state = QtCore.pyqtSignal(str, object)

    def __init__(self, com_manager, parent=None):
        super().__init__(parent)
        self.com_manager = com_manager
        # connect handle slot
        self.timeout.connect(self._handle_timeout)
        self.start(500)

    def _handle_timeout(self):
        while not self.com_manager.res_queue.empty():
            res = self.com_manager.res_queue.get()
            if res.com_type is ComType.install:
                self.mj_installed.emit(res.key)
            elif res.com_type is ComType.qued:
                self.mj_qued.emit(res.key)
            elif res.com_type is ComType.pause:
                self.mj_paused.emit(res.key)
            elif res.com_type is ComType.resume:
                self.mj_resumed.emit(res.key)
            elif res.com_type is ComType.results:
                if res.data:
                    self.mj_result.emit(res.key, res.data)
            elif res.com_type is ComType.state:
                if res.data:
                    self.mj_state.emit(res.key, res.data)
            elif res.com_type is ComType.stop:
                self.mj_stopped.emit(res.key)
            else:
                raise Exception("Response type not recognized")
