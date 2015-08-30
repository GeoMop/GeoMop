#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class UiMultijobTable(QtWidgets.QTableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.resizeRowsToContents()
        self.headers = ["Name", "Insert Time", "Run Time", "Run Interval",
                        "Status"]
        self.setColumnCount(len(self.headers))
        self.setRowCount(len(self.headers))
        self.setHorizontalHeaderLabels(self.headers)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch)
