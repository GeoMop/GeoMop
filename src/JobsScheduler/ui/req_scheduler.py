# -*- coding: utf-8 -*-
"""
Timer scheduler periodic request
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer

from ui.com_manager import ComType


class ReqScheduler(QTimer):
    mj_stoped = QtCore.pyqtSignal(str)
    mj_installed = QtCore.pyqtSignal(str)

    def __init__(self, com_manager, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.com_manager = com_manager
        # connect handle slot
        self.timeout.connect(self._handle_timeout)
        self.start(20)

    def _handle_timeout(self):
        for key in self.main_window.data.multijobs:
            if self.com_manager.is_installed(key):
                self.com_manager.state(key)
        cur_item = self.main_window.ui.overviewWidget.currentItem()
        if cur_item:
            key = cur_item.text(0)
            if self.com_manager.is_installed(key):
                self.com_manager.results(key)
