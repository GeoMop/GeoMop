#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets
from ui.actions.main_window_actions import *
from ui.menus.main_window_menus import MainWindowMenuBar
from ui.panels.multijob_overview import MultiJobOverview
from ui.panels.multijob_infotab import MultiJobInfoTab
from ui.dialogs.multijob_dialog import MultiJobDialog
from ui.dialogs.ssh_presets import SshPresets
from ui.dialogs.pbs_presets import PbsPresets
import config as cfg
import uuid


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    multijobs_changed = QtCore.pyqtSignal(dict)

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
        self.multijobs_changed.connect(self.ui.multiJobOverview.reload_view)
        self.multijobs_changed.connect(self.data.save_mj)

        # ssh presets
        self.ssh_presets_dlg = SshPresets(self, self.data.shh_presets)
        self.ui.actionSshPresets.triggered.connect(
            self.ssh_presets_dlg.show)
        self.ssh_presets_dlg.presets_changed.connect(self.data.save_ssh)

        # ssh presets
        self.pbs_presets_dlg = PbsPresets(self, self.data.pbs_presets)
        self.ui.actionPbsPresets.triggered.connect(
            self.pbs_presets_dlg.show)
        self.pbs_presets_dlg.presets_changed.connect(self.data.save_pbs)

        # ssh presets
        self.resource_presets_dlg = PbsPresets(self,
                                               self.data.resources_presets)
        self.ui.actionResourcesPresets.triggered.connect(
            self.resource_presets_dlg.show)
        self.resource_presets_dlg.presets_changed.connect(
            self.data.save_resources)

        # connect exit action
        self.ui.actionExit.triggered.connect(QtWidgets.QApplication.quit)

        # reload view
        self.ui.multiJobOverview.reload_view(self.data.multijobs)

    def _handle_add_multijob_action(self):
        self.mj_dlg.set_purpose(MultiJobDialog.PURPOSE_ADD)
        self.mj_dlg.show()

    def _handle_edit_multijob_action(self):
        if self.data.multijobs:
            self.mj_dlg.set_purpose(self.mj_dlg.PURPOSE_EDIT)
            key = self.ui.multiJobOverview.currentItem().text(0)
            data = list(self.data.multijobs[key])  # list to make a copy
            data.insert(0, key)  # insert id
            self.mj_dlg.set_data(tuple(data))
            self.mj_dlg.show()

    def _handle_copy_multijob_action(self):
        if self.data.multijobs:
            self.mj_dlg.set_purpose(self.mj_dlg.PURPOSE_COPY)
            key = self.ui.multiJobOverview.currentItem().text(0)
            data = list(self.data.multijobs[key])
            data.insert(0, None)  # insert empty id
            data[1] = self.mj_dlg.PURPOSE_COPY_PREFIX + " " + data[1]
            self.mj_dlg.set_data(tuple(data))
            self.mj_dlg.show()

    def _handle_delete_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.multiJobOverview.currentItem().text(0)
            self.data.multijobs.pop(key)  # delete by key
            self.multijobs_changed.emit(self.data.multijobs)

    def handle_multijob_dialog(self, purpose, data):
        if purpose != self.mj_dlg.PURPOSE_EDIT:
            key = str(uuid.uuid1())
            self.data.multijobs[key] = list(data[1:])
        else:
            self.data.multijobs[data[0]] = list(data[1:])
        self.multijobs_changed.emit(self.data.multijobs)


class DataMainWindow(object):
    MJ_DIR = "mjwewdw"
    SSH_DIR = "sswqeqwehdw"
    PBS_DIR = "pbswqedw"
    RESOURCE_DIR = "resowqeqweurcedw"

    def __init__(self):
        self.multijobs = cfg.get_config_file("list", self.MJ_DIR)
        if not self.multijobs:
            self.multijobs = dict()
        self.shh_presets = cfg.get_config_file("list", self.SSH_DIR)
        if not self.shh_presets:
            self.shh_presets = dict()
        self.pbs_presets = cfg.get_config_file("list", self.PBS_DIR)
        if not self.pbs_presets:
            self.pbs_presets = dict()
        self.resources_presets = cfg.get_config_file("list", self.RESOURCE_DIR)
        if not self.resources_presets:
            self.resources_presets = dict()

    def save_mj(self):
        print("Mj saved")
        cfg.save_config_file("list", self.multijobs, self.MJ_DIR)

    def save_ssh(self):
        print("Ssh saved")
        cfg.save_config_file("list", self.shh_presets, self.SSH_DIR)

    def save_pbs(self):
        print("Pbs saved")
        cfg.save_config_file("list", self.pbs_presets, self.PBS_DIR)

    def save_resources(self):
        print("Resource saved")
        cfg.save_config_file("list", self.resources_presets, self.RESOURCE_DIR)

    def save_all(self, mj, ssh, pbs, resource):
        print("All saved")
        pass


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
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")

        # actions
        self.actionExit = ActionExit(main_window)

        self.actionAddMultiJob = ActionAddMultiJob(main_window)
        self.actionEditMultiJob = ActionEditMultiJob(main_window)
        self.actionCopyMultiJob = ActionCopyMultiJob(main_window)
        self.actionDeleteMultiJob = ActionDeleteMultiJob(main_window)
        # ----
        self.actionRunMultiJob = ActionRunMultiJob(main_window)
        self.actionPauseMultiJob = ActionPauseMultiJob(main_window)
        self.actionStopMultiJob = ActionStopMultiJob(main_window)
        self.actionRestartMultiJob = ActionRestartMultiJob(main_window)

        self.actionSshPresets = ActionSshPresets(main_window)
        self.actionPbsPresets = ActionPbsPresets(main_window)
        self.actionResourcesPresets = ActionResourcesPresets(main_window)

        # menuBar
        self.menuBar = MainWindowMenuBar(main_window)
        main_window.setMenuBar(self.menuBar)

        # bind actions to menus
        self.menuBar.menu.addAction(self.actionExit)
        self.menuBar.multiJob.addAction(self.actionAddMultiJob)
        self.menuBar.multiJob.addAction(self.actionEditMultiJob)
        self.menuBar.multiJob.addAction(self.actionCopyMultiJob)
        self.menuBar.multiJob.addAction(self.actionDeleteMultiJob)
        self.menuBar.multiJob.addSeparator()
        self.menuBar.multiJob.addAction(self.actionRunMultiJob)
        self.menuBar.multiJob.addAction(self.actionPauseMultiJob)
        self.menuBar.multiJob.addAction(self.actionStopMultiJob)
        self.menuBar.multiJob.addAction(self.actionRestartMultiJob)
        self.menuBar.settings.addAction(self.actionSshPresets)
        self.menuBar.settings.addAction(self.actionPbsPresets)
        self.menuBar.settings.addAction(self.actionResourcesPresets)

        # multiJob Overview panel
        self.multiJobOverview = MultiJobOverview(self.centralwidget)
        self.mainVerticalLayout.addWidget(self.multiJobOverview)

        # multiJobInfoTab panel
        self.multiJobInfoTab = MultiJobInfoTab(self.centralwidget)
        self.mainVerticalLayout.addWidget(self.multiJobInfoTab)

        # set central widget
        main_window.setCentralWidget(self.centralwidget)

