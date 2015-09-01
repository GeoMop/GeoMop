#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets
from ui.panels.multijob_overview import MultiJobOverview
from ui.panels.multijob_infotab import MultiJobInfoTab


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)
        self.show()


class UiMainWindow(object):
    """
    Jobs Scheduler UI
    """
    def setup_ui(self, main_window):
        """
        Setup basic UI
        """
        # main window
        main_window.resize(1014, 702)
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle('Jobs Scheduler')

        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")

        # MultiJob Overview panel
        self.multiJobOverview = MultiJobOverview(self.centralwidget)
        self.verticalLayout.addWidget(self.multiJobOverview)

        # MultiJobInfoTab panel
        self.multiJobInfoTab = MultiJobInfoTab(self.centralwidget)
        self.verticalLayout.addWidget(self.multiJobInfoTab)

        self.verticalLayout_2.addLayout(self.verticalLayout)
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1014, 27))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setTitle("Menu")
        self.menuMenu.setObjectName("menuMenu")
        self.menuMultiJob = QtWidgets.QMenu(self.menubar)
        self.menuMultiJob.setTitle("MultiJob")
        self.menuMultiJob.setObjectName("menuMultiJob")
        self.menuSettings = QtWidgets.QMenu(self.menubar)
        self.menuSettings.setTitle("Settings")
        self.menuSettings.setObjectName("menuSettings")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.toolBar = QtWidgets.QToolBar(main_window)
        self.toolBar.setWindowTitle("toolBar")
        self.toolBar.setObjectName("toolBar")
        main_window.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.actionExit = QtWidgets.QAction(main_window)
        self.actionExit.setText("Exit")
        self.actionExit.setShortcut("Ctrl+Q")
        self.actionExit.setObjectName("actionExit")
        self.actionAdd = QtWidgets.QAction(main_window)
        self.actionAdd.setText("Add")
        self.actionAdd.setShortcut("Alt+A")
        self.actionAdd.setObjectName("actionAdd")
        self.actionCopy = QtWidgets.QAction(main_window)
        self.actionCopy.setText("Copy")
        self.actionCopy.setShortcut("Alt+C")
        self.actionCopy.setObjectName("actionCopy")
        self.actionEdit = QtWidgets.QAction(main_window)
        self.actionEdit.setText("Edit")
        self.actionEdit.setShortcut("Alt+E")
        self.actionEdit.setObjectName("actionEdit")
        self.actionResources = QtWidgets.QAction(main_window)
        self.actionResources.setText("Resources")
        self.actionResources.setShortcut("Shift+R")
        self.actionResources.setObjectName("actionResources")
        self.actionSSH_Connections = QtWidgets.QAction(main_window)
        self.actionSSH_Connections.setText("SSH Connections")
        self.actionSSH_Connections.setShortcut("Shift+S")
        self.actionSSH_Connections.setObjectName("actionSSH_Connections")
        self.actionPBSs = QtWidgets.QAction(main_window)
        self.actionPBSs.setText("PBSs")
        self.actionPBSs.setShortcut("Shift+P")
        self.actionPBSs.setObjectName("actionPBSs")
        self.actionDelete = QtWidgets.QAction(main_window)
        self.actionDelete.setText("Delete")
        self.actionDelete.setShortcut("Alt+D")
        self.actionDelete.setObjectName("actionDelete")
        self.actionRun = QtWidgets.QAction(main_window)
        self.actionRun.setText("Run")
        self.actionRun.setShortcut("Alt+R")
        self.actionRun.setObjectName("actionRun")
        self.actionStop = QtWidgets.QAction(main_window)
        self.actionStop.setText("Stop")
        self.actionStop.setShortcut("Alt+S")
        self.actionStop.setObjectName("actionStop")
        self.actionPause = QtWidgets.QAction(main_window)
        self.actionPause.setText("Pause")
        self.actionPause.setShortcut("Alt+P")
        self.actionPause.setObjectName("actionPause")
        self.actionRestart = QtWidgets.QAction(main_window)
        self.actionRestart.setText("Restart")
        self.actionRestart.setShortcut("Alt+R")
        self.actionRestart.setObjectName("actionRestart")
        self.menuMenu.addAction(self.actionExit)
        self.menuMultiJob.addAction(self.actionAdd)
        self.menuMultiJob.addAction(self.actionEdit)
        self.menuMultiJob.addAction(self.actionCopy)
        self.menuMultiJob.addAction(self.actionDelete)
        self.menuMultiJob.addSeparator()
        self.menuMultiJob.addAction(self.actionRun)
        self.menuMultiJob.addAction(self.actionPause)
        self.menuMultiJob.addAction(self.actionStop)
        self.menuMultiJob.addAction(self.actionRestart)
        self.menuSettings.addAction(self.actionSSH_Connections)
        self.menuSettings.addAction(self.actionPBSs)
        self.menuSettings.addAction(self.actionResources)
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuMultiJob.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
