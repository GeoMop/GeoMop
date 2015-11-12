# -*- coding: utf-8 -*-
"""
Timer that gets data from threads and notifies main window to refresh view
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer


class WindowRefresher(QTimer):
    results_changed = QtCore.pyqtSignal(dict)
    main_key = None

    def __init__(self, data_reloader, parent=None):
        super().__init__(parent)
        self.data_reloader = data_reloader
        self._result = None
        # connect handle slot
        self.timeout.connect(self._handle_timeout)

    def _handle_timeout(self):
        if not self.data_reloader.needs_reload.is_set():
            self._result = copy.deepcopy(self.data_reloader.results)
            self.results_changed.emit(self._result)
            self.data_reloader.main_key = self.main_key
            self.data_reloader.needs_reload.set()
        else:
            return
