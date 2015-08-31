#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class UiMultijobInfotab(QtWidgets.QTabWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.addTab(self.tab_2, "")

        # labels
        self.setTabText(0, "TAB1")
        self.setTabText(1, "TAB2")
