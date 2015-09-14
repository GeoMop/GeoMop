# -*- coding: utf-8 -*-
"""
Main window menus
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class MainWindowMenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super(MainWindowMenuBar, self).__init__(parent)
        self.setObjectName("MainWindowMenuBar")

        self.menu = QtWidgets.QMenu(self)
        self.menu.setTitle("Menu")
        self.menu.setObjectName("menu")

        self.multiJob = QtWidgets.QMenu(self)
        self.multiJob.setTitle("MultiJob")
        self.multiJob.setObjectName("multiJob")

        self.settings = QtWidgets.QMenu(self)
        self.settings.setTitle("Settings")
        self.settings.setObjectName("settings")

        self.addAction(self.menu.menuAction())
        self.addAction(self.multiJob.menuAction())
        self.addAction(self.settings.menuAction())
