# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import uuid

from PyQt5 import QtCore

from ui.actions.main_window_actions import *
from ui.dialogs.resource_presets import ResourcePresets
from ui.menus.main_window_menus import MainWindowMenuBar
from ui.panels.multijob_overview import MultiJobOverview
from ui.panels.multijob_infotab import MultiJobInfoTab
from ui.dialogs.multijob_dialog import MultiJobDialog
from ui.dialogs.ssh_presets import SshPresets
from ui.dialogs.pbs_presets import PbsPresets
from communication import Communicator


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    multijobs_changed = QtCore.pyqtSignal(dict)
    tabs_data_changed = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, data=None, data_reloader=None):
        super().__init__(parent)
        self.data = data
        self.data_reloader = data_reloader
        self.data_reloader.notify_data_changed = self._handle_data_changed

        # setup UI
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)

        self.tabs_data_changed.connect(self.ui.multiJobInfoTab.reload_view)

        # init dialogs
        self.mj_dlg = MultiJobDialog(parent=self,
                                     resources=self.data.resource_presets)
        self.ssh_presets_dlg = SshPresets(parent=self,
                                          presets=self.data.ssh_presets)
        self.pbs_presets_dlg = PbsPresets(parent=self,
                                          presets=self.data.pbs_presets)
        self.resource_presets_dlg \
            = ResourcePresets(parent=self,
                              presets=self.data.resource_presets,
                              pbs=self.data.pbs_presets,
                              ssh=self.data.ssh_presets)

        # multijob dialog
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
        self.multijobs_changed.connect(self.data.multijobs.save)
        self.resource_presets_dlg.presets_changed.connect(
            self.mj_dlg.set_resource_presets)

        # ssh presets
        self.ui.actionSshPresets.triggered.connect(
            self.ssh_presets_dlg.show)
        self.ssh_presets_dlg.presets_changed.connect(
            self.data.ssh_presets.save)

        # pbs presets
        self.ui.actionPbsPresets.triggered.connect(
            self.pbs_presets_dlg.show)
        self.pbs_presets_dlg.presets_changed.connect(
            self.data.pbs_presets.save)

        # resource presets
        self.ui.actionResourcesPresets.triggered.connect(
            self.resource_presets_dlg.show)
        self.resource_presets_dlg.presets_changed.connect(
            self.data.resource_presets.save)
        self.pbs_presets_dlg.presets_changed.connect(
            self.resource_presets_dlg.presets_dlg.set_pbs_presets)
        self.ssh_presets_dlg.presets_changed.connect(
            self.resource_presets_dlg.presets_dlg.set_ssh_presets)

        # connect exit action
        self.ui.actionExit.triggered.connect(QtWidgets.QApplication.quit)

        # connect multijob action
        self.ui.actionRunMultiJob.triggered.connect(
            self._handle_run_multijob_action)

        # reload view
        self.ui.multiJobOverview.reload_view(self.data.multijobs)

    def _handle_add_multijob_action(self):
        self.mj_dlg.set_purpose(MultiJobDialog.PURPOSE_ADD)
        self.mj_dlg.show()

    def _handle_edit_multijob_action(self):
        if self.data.multijobs:
            self.mj_dlg.set_purpose(self.mj_dlg.PURPOSE_EDIT)
            key = self.ui.multiJobOverview.currentItem().text(0)
            data = list(self.data.multijobs[key]["preset"])
            data.insert(0, key)  # insert id
            self.mj_dlg.set_data(tuple(data))
            self.mj_dlg.show()

    def _handle_copy_multijob_action(self):
        if self.data.multijobs:
            self.mj_dlg.set_purpose(self.mj_dlg.PURPOSE_COPY)
            key = self.ui.multiJobOverview.currentItem().text(0)
            data = list(self.data.multijobs[key]["preset"])
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
            key = str(uuid.uuid4())
            self.data.multijobs[key] = dict()
            self.data.multijobs[key]["preset"] = list(data[1:])
        else:
            self.data.multijobs[data[0]]["preset"] = list(data[1:])
        self.multijobs_changed.emit(self.data.multijobs)

    def _handle_run_multijob_action(self):
        key = self.ui.multiJobOverview.currentItem().text(0)
        app_conf = self.data.build_config_files(key)
        communicator = Communicator(app_conf)
        self.data_reloader.install_communicator(key, communicator)

    def _handle_data_changed(self, key):
        self.tabs_data_changed.emit(self.data.multijobs[key]["logs"])


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

