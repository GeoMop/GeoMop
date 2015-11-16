# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import uuid

import time
from PyQt5 import QtCore

from communication import Communicator
from data.states import TaskStatus
from ui.actions.main_window_actions import *
from ui.dialogs.env_presets import EnvPresets
from ui.dialogs.multijob_dialog import MultiJobDialog
from ui.dialogs.pbs_presets import PbsPresets
from ui.dialogs.resource_presets import ResourcePresets
from ui.dialogs.ssh_presets import SshPresets
from ui.main_window_refresher import WindowRefresher
from ui.menus.main_window_menus import MainWindowMenuBar
from ui.panels.overview import Overview
from ui.panels.tabs import Tabs


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    multijobs_changed = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None, data=None, data_reloader=None):
        super().__init__(parent)
        # setup UI
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)

        self.data = data
        self.data_reloader = data_reloader
        self.windows_refresher = WindowRefresher(parent=self,
                                                 data_reloader=data_reloader)
        self.windows_refresher.results_changed.connect(
            self.handle_results_changed)

        self.ui.overviewWidget.currentItemChanged.connect(
            self._handle_mj_selection_changed)

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
                              ssh=self.data.ssh_presets,
                              env=self.data.env_presets)

        self.env_presets_dlg = EnvPresets(parent=self,
                                          presets=self.data.env_presets)

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
        self.multijobs_changed.connect(self.ui.overviewWidget.reload_view)
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

        # env presets
        self.ui.actionEnvPresets.triggered.connect(
            self.env_presets_dlg.show)
        self.env_presets_dlg.presets_changed.connect(
            self.data.env_presets.save)

        # resource presets
        self.ui.actionResourcesPresets.triggered.connect(
            self.resource_presets_dlg.show)
        self.resource_presets_dlg.presets_changed.connect(
            self.data.resource_presets.save)
        self.pbs_presets_dlg.presets_changed.connect(
            self.resource_presets_dlg.presets_dlg.set_pbs_presets)
        self.ssh_presets_dlg.presets_changed.connect(
            self.resource_presets_dlg.presets_dlg.set_ssh_presets)
        self.env_presets_dlg.presets_changed.connect(
            self.resource_presets_dlg.presets_dlg.set_env_presets)

        # connect exit action
        self.ui.actionExit.triggered.connect(QtWidgets.QApplication.quit)

        # connect multijob action
        self.ui.actionRunMultiJob.triggered.connect(
            self._handle_run_multijob_action)

        # reload view
        self.ui.overviewWidget.reload_view(self.data.multijobs)

        self.windows_refresher.start(1)

    def _handle_mj_selection_changed(self, current, previous):
        # self.windows_refresher.main_key = current.text(0)
        pass

    def _handle_add_multijob_action(self):
        self.mj_dlg.set_purpose(MultiJobDialog.PURPOSE_ADD)
        self.mj_dlg.show()

    def _handle_edit_multijob_action(self):
        if self.data.multijobs:
            self.mj_dlg.set_purpose(self.mj_dlg.PURPOSE_EDIT)
            key = self.ui.overviewWidget.currentItem().text(0)
            data = list(self.data.multijobs[key]["preset"])
            data.insert(0, key)  # insert id
            self.mj_dlg.set_data(tuple(data))
            self.mj_dlg.show()

    def _handle_copy_multijob_action(self):
        if self.data.multijobs:
            self.mj_dlg.set_purpose(self.mj_dlg.PURPOSE_COPY)
            key = self.ui.overviewWidget.currentItem().text(0)
            data = list(self.data.multijobs[key]["preset"])
            data.insert(0, None)  # insert empty id
            data[1] = self.mj_dlg.PURPOSE_COPY_PREFIX + " " + data[1]
            self.mj_dlg.set_data(tuple(data))
            self.mj_dlg.show()

    def _handle_delete_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            self.data.multijobs.pop(key)  # delete by key
            self.multijobs_changed.emit(self.data.multijobs)

    def handle_multijob_dialog(self, purpose, data):
        state = {
            "name": data[1],
            "insert_time": None,
            "run_time": None,
            "run_interval": None,
            "status": TaskStatus.none.name
        }
        if purpose != self.mj_dlg.PURPOSE_EDIT:
            key = str(uuid.uuid4())
            self.data.multijobs[key] = dict()
            self.data.multijobs[key]["preset"] = list(data[1:])
            self.data.multijobs[key]["state"] = state
        else:
            self.data.multijobs[data[0]]["preset"] = list(data[1:])
            self.data.multijobs[data[0]]["state"] = state
        self.multijobs_changed.emit(self.data.multijobs)

    def _handle_run_multijob_action(self):
        key = self.ui.overviewWidget.currentItem().text(0)
        self.data.multijobs[key]["state"]["status"] = \
            TaskStatus.installation.name
        # self.multijobs_changed.emit(self.data.multijobs)
        app_conf = self.data.build_config_files(key)
        communicator = Communicator(app_conf)
        self.data_reloader.install_communicator(key, communicator)

    def handle_results_changed(self, results):
        try:
            key = self.ui.overviewWidget.currentItem().text(0)
            if results[key].get("state", None):
                state = results[key]["state"]
                print("UI state valid")
                newstate = {
                    "name": state.name,
                    "insert_time": time.ctime(state.insert_time),
                    "run_time": time.ctime(state.start_time),
                    "run_interval": state.run_interval,
                    "status": state.status.name
                }
                self.data.multijobs[key]["state"] = newstate
                self.multijobs_changed.emit(self.data.multijobs)
            self.ui.tabWidget.reload_view(results[key])
        except KeyError as keyerr:
            pass
        except AttributeError as atrerr:
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
        self.actionEnvPresets = ActionEnvPresets(main_window)

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
        self.menuBar.settings.addAction(self.actionEnvPresets)

        # multiJob Overview panel
        self.overviewWidget = Overview(self.centralwidget)
        self.mainVerticalLayout.addWidget(self.overviewWidget)

        # tabWidget panel
        self.tabWidget = Tabs(self.centralwidget)
        self.mainVerticalLayout.addWidget(self.tabWidget)

        # set central widget
        main_window.setCentralWidget(self.centralwidget)

