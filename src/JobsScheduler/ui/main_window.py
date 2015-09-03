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
from ui.dialogs.multijob import MultiJobDialog
import uuid


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = DataMainWindow()

        # setup UI
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)

        # init dialogs
        # multijob dialog
        self.mj_dlg = MultiJobDialog(self)
        self.ui.actionAddMultiJob.triggered.connect(
            self._handle_add_multijob_action)
        self.ui.actionEditMultiJob.triggered.connect(
            self._handle_edit_multijob_action)
        self.ui.actionCopyMultiJob.triggered.connect(
            self._handle_copy_multijob_action)
        self.ui.actionDeleteMultiJob.triggered.connect(
            self._handle_delete_multijob_action)
        self.mj_dlg.accepted.connect(self.handle_multijob_dialog)

        # set data
        self.ui.multiJobOverview.set_data(self.data.multi_jobs)

    def _handle_add_multijob_action(self):
        self.mj_dlg.set_purpose(MultiJobDialog.PURPOSE_ADD)
        self.mj_dlg.show()

    def _handle_edit_multijob_action(self):
        if self.data.multi_jobs:
            self.mj_dlg.set_purpose(MultiJobDialog.PURPOSE_EDIT)
            index = self.ui.multiJobOverview.indexOfTopLevelItem(
                self.ui.multiJobOverview.currentItem())
            self.mj_dlg.set_data(list(self.data.multi_jobs[index]))
            self.mj_dlg.show()

    def _handle_copy_multijob_action(self):
        if self.data.multi_jobs:
            self.mj_dlg.set_purpose(MultiJobDialog.PURPOSE_COPY)
            index = self.ui.multiJobOverview.indexOfTopLevelItem(
                self.ui.multiJobOverview.currentItem())
            data = list(self.data.multi_jobs[index])
            data[0] = None
            data[1] = "Copy of " + data[1]
            self.mj_dlg.set_data(data)
            self.mj_dlg.show()

    def _handle_delete_multijob_action(self):
        if self.data.multi_jobs:
            index = self.ui.multiJobOverview.indexOfTopLevelItem(
                self.ui.multiJobOverview.currentItem())
            self.data.multi_jobs.pop(index)
            self.ui.multiJobOverview.set_data(self.data.multi_jobs)

    def handle_multijob_dialog(self, purpose, data):
        if purpose != MultiJobDialog.PURPOSE_EDIT:
            data[0] = str(uuid.uuid4())
            self.data.multi_jobs.append(data)
        else:
            for i, item in enumerate(self.data.multi_jobs):
                if item[0] == data[0]:
                    self.data.multi_jobs[i] = data
        self.ui.multiJobOverview.set_data(self.data.multi_jobs)


class DataMainWindow(object):
    def __init__(self):
        self.multi_jobs = list()
        #self.pbs_presets
        #self.shh_presets


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

        # Add MultiJob action
        self.actionAddMultiJob = QtWidgets.QAction(main_window)
        self.actionAddMultiJob.setText("Add")
        self.actionAddMultiJob.setShortcut("Alt+A")
        self.actionAddMultiJob.setObjectName("actionAddMultiJob")

        # Edit MultiJob action
        self.actionEditMultiJob = QtWidgets.QAction(main_window)
        self.actionEditMultiJob.setText("Edit")
        self.actionEditMultiJob.setShortcut("Alt+E")
        self.actionEditMultiJob.setObjectName("actionEditMultiJob")

        # Copy MultiJob action
        self.actionCopyMultiJob = QtWidgets.QAction(main_window)
        self.actionCopyMultiJob.setText("Copy")
        self.actionCopyMultiJob.setShortcut("Alt+C")
        self.actionCopyMultiJob.setObjectName("actionCopyMultiJob")

        # Delete MultiJob action
        self.actionDeleteMultiJob = QtWidgets.QAction(main_window)
        self.actionDeleteMultiJob.setText("Delete")
        self.actionDeleteMultiJob.setShortcut("Alt+D")
        self.actionDeleteMultiJob.setObjectName("actionDeleteMultiJob")

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

        # bind actions to menus
        self.menuMenu.addAction(self.actionExit)
        self.menuMultiJob.addAction(self.actionAddMultiJob)
        self.menuMultiJob.addAction(self.actionEditMultiJob)
        self.menuMultiJob.addAction(self.actionCopyMultiJob)
        self.menuMultiJob.addAction(self.actionDeleteMultiJob)
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

