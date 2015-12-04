# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import os
from PyQt5 import QtCore
from communication import Communicator, Installation
from data.states import TaskStatus
from ui.actions.main_menu_actions import *
from ui.data.config_factory import ConfigBuilder
from ui.data.mj_data import MultiJob
from ui.data.preset_data import Id
from ui.dialogs.env_presets import EnvPresets
from ui.dialogs.multijob_dialog import MultiJobDialog
from ui.dialogs.pbs_presets import PbsPresets
from ui.dialogs.resource_presets import ResourcePresets
from ui.dialogs.ssh_presets import SshPresets
from ui.req_scheduler import ReqScheduler
from ui.res_handler import ResHandler
from ui.menus.main_menu_bar import MainMenuBar
from ui.panels.overview import Overview
from ui.panels.tabs import Tabs


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    multijobs_changed = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None, data=None, com_manager=None):
        super().__init__(parent)
        # setup UI
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)

        self.data = data
        self.com_manager = com_manager
        self.req_scheduler = ReqScheduler(parent=self,
                                          com_manager=self.com_manager)
        self.res_handler = ResHandler(parent=self,
                                      com_manager=self.com_manager)

        self.res_handler.mj_installed.connect(
            self.handle_mj_installed)

        self.res_handler.mj_result.connect(
            self.handle_mj_result)

        self.res_handler.mj_state.connect(
            self.handle_mj_state)

        self.res_handler.mj_paused.connect(
            self.handle_mj_paused)

        self.res_handler.mj_resumed.connect(
            self.handle_mj_resumed)

        self.res_handler.mj_stopped.connect(
            self.handle_mj_stopped)

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
        self.ui.menuBar.multiJob.actionAddMultiJob.triggered.connect(
            self._handle_add_multijob_action)
        self.ui.menuBar.multiJob.actionEditMultiJob.triggered.connect(
            self._handle_edit_multijob_action)
        self.ui.menuBar.multiJob.actionCopyMultiJob.triggered.connect(
            self._handle_copy_multijob_action)
        self.ui.menuBar.multiJob.actionDeleteMultiJob.triggered.connect(
            self._handle_delete_multijob_action)
        self.mj_dlg.accepted.connect(self.handle_multijob_dialog)
        self.multijobs_changed.connect(self.ui.overviewWidget.reload_items)
        self.multijobs_changed.connect(self.data.multijobs.save)
        self.resource_presets_dlg.presets_changed.connect(
            self.mj_dlg.set_resource_presets)

        # ssh presets
        self.ui.menuBar.settings.actionSshPresets.triggered.connect(
            self.ssh_presets_dlg.show)
        self.ssh_presets_dlg.presets_changed.connect(
            self.data.ssh_presets.save)

        # pbs presets
        self.ui.menuBar.settings.actionPbsPresets.triggered.connect(
            self.pbs_presets_dlg.show)
        self.pbs_presets_dlg.presets_changed.connect(
            self.data.pbs_presets.save)

        # env presets
        self.ui.menuBar.settings.actionEnvPresets.triggered.connect(
            self.env_presets_dlg.show)
        self.env_presets_dlg.presets_changed.connect(
            self.data.env_presets.save)

        # resource presets
        self.ui.menuBar.settings.actionResourcesPresets.triggered.connect(
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
        self.ui.menuBar.app.actionExit.triggered.connect(
            QtWidgets.QApplication.quit)

        # connect multijob run action
        self.ui.menuBar.multiJob.actionRunMultiJob.triggered.connect(
            self._handle_run_multijob_action)

        # connect multijob stop action
        self.ui.menuBar.multiJob.actionPauseMultiJob.triggered.connect(
            self._handle_pause_multijob_action)

        # connect multijob resume action
        self.ui.menuBar.multiJob.actionResumeMultiJob.triggered.connect(
            self._handle_resume_multijob_action)

        # connect multijob stop action
        self.ui.menuBar.multiJob.actionStopMultiJob.triggered.connect(
            self._handle_stop_multijob_action)

        # connect multijob restart action
        self.ui.menuBar.multiJob.actionRestartMultiJob.triggered.connect(
            self._handle_restart_multijob_action)

        # connect current multijob changed
        self.ui.overviewWidget.currentItemChanged.connect(
            self.update_ui_locks)

        # reload view
        self.ui.overviewWidget.reload_items(self.data.multijobs)

    def update_ui_locks(self, current, previous=None):
        if current is None:
            self.ui.menuBar.multiJob.lock_by_status(None)
        else:
            status = self.data.multijobs[current.text(0)].state.status
            self.ui.menuBar.multiJob.lock_by_status(status)
            mj = self.data.multijobs[current.text(0)]
            self.ui.tabWidget.reload_view(mj)

    def _handle_add_multijob_action(self):
        self.mj_dlg.exec_add()

    def _handle_edit_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            preset = self.data.multijobs[key].preset
            data = {
                "key": key,
                "preset": preset
            }
            self.mj_dlg.exec_edit(data)

    def _handle_copy_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            preset = copy.deepcopy(self.data.multijobs[key].preset)
            preset.name = self.presets_dlg.\
                PURPOSE_COPY_PREFIX + " " + preset.name
            data = {
                "key": key,
                "preset": preset
            }
            self.presets_dlg.exec_copy(data)

    def _handle_delete_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            self.data.multijobs.pop(key)  # delete by key
            self.multijobs_changed.emit(self.data.multijobs)

    def handle_multijob_dialog(self, purpose, data):
        if purpose != self.mj_dlg.PURPOSE_EDIT:
            key = Id.get_id()
            self.data.multijobs[key] = MultiJob(data["preset"])
        else:
            # Todo properly edit state, change folder name etc.
            self.data.multijobs[data["key"]] = MultiJob(data["preset"])
        self.multijobs_changed.emit(self.data.multijobs)

    def _handle_run_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        state = self.data.multijobs[key].state
        state.status = TaskStatus.installation
        self.ui.overviewWidget.update_item(key, state)

        self.update_ui_locks(current)

        conf_builder = ConfigBuilder(self.data)
        app_conf = conf_builder.build(key)
        Communicator.lock_installation(app_conf)
        com = Communicator(app_conf)
        # reload log
        res_path = Installation.get_result_dir_static(com.mj_name)
        log_path = os.path.join(res_path, "log")
        self.ui.tabWidget.ui.logsTab.reload_view(log_path)
        self.com_manager.install(key, com)
        Communicator.unlock_installation(com.mj_name)

    def _handle_pause_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        state = self.data.multijobs[key].state
        state.status = TaskStatus.pausing
        self.ui.overviewWidget.update_item(key, state)

        self.update_ui_locks(current)

        self.com_manager.pause(key)

    def _handle_resume_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        state = self.data.multijobs[key].state
        state.status = TaskStatus.resuming
        self.ui.overviewWidget.update_item(key, state)

        self.update_ui_locks(current)

        self.com_manager.resume(key)

    def _handle_stop_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        state = self.data.multijobs[key].state
        state.status = TaskStatus.stopping
        self.ui.overviewWidget.update_item(key, state)

        self.update_ui_locks(current)
        self.com_manager.stop(key)
        Communicator.unlock_installation(
            self.com_manager.get_communicator(key).mj_name)

    def handle_terminate(self):
        mj = self.data.multijobs
        for key in self.data.multijobs:
            state = mj[key].state
            state.status = TaskStatus.none
        self.com_manager.terminate()
        print("Exiting")

    def _handle_restart_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        state = self.data.multijobs[key].state
        state.status = TaskStatus.stopping
        self.ui.overviewWidget.update_item(key, state)

        self.update_ui_locks(current)

        self.com_manager.restart(key)

    def handle_mj_installed(self, key):
        state = self.data.multijobs[key].state
        state.status = TaskStatus.running

        self.ui.overviewWidget.update_item(key, state)
        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_paused(self, key):
        state = self.data.multijobs[key].state
        state.status = TaskStatus.paused

        self.ui.overviewWidget.update_item(key, state)
        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_resumed(self, key):
        state = self.data.multijobs[key].state
        state.status = TaskStatus.running

        self.ui.overviewWidget.update_item(key, state)
        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_stopped(self, key):
        state = self.data.multijobs[key].state
        state.status = TaskStatus.none

        self.ui.overviewWidget.update_item(key, state)
        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_state(self, key, state):
        if state.status == TaskStatus.running:
            mj_state = self.data.multijobs[key].state
            mj_state.update(state)
            self.ui.overviewWidget.update_item(key, mj_state)
        elif state.status == TaskStatus.ready:
            current = self.ui.overviewWidget.currentItem()
            state = self.data.multijobs[key].state
            state.status = TaskStatus.stopping
            self.ui.overviewWidget.update_item(key, state)
            self.update_ui_locks(current)
            self.com_manager.stop(key)

    def handle_mj_result(self, key, result):
        mj = self.data.multijobs[key]
        mj.jobs = result["jobs"]
        mj.logs = result["logs"]
        mj.conf = result["conf"]
        mj.res = result["res"]
        current = self.ui.overviewWidget.currentItem()
        if current.text(0) == key:
            self.ui.tabWidget.reload_view(mj)


class UiMainWindow(object):
    """
    Jobs Scheduler UI
    """
    def setup_ui(self, main_window):
        """
        Setup basic UI
        """
        # main window
        main_window.resize(1154, 702)
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle('Jobs Scheduler')

        # central widget and layout
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainVerticalLayout.setObjectName("mainVerticalLayout")

        # menuBar
        self.menuBar = MainMenuBar(main_window)
        main_window.setMenuBar(self.menuBar)

        # multiJob Overview panel
        self.overviewWidget = Overview(self.centralwidget)
        self.mainVerticalLayout.addWidget(self.overviewWidget)

        # tabWidget panel
        self.tabWidget = Tabs(self.centralwidget)
        self.mainVerticalLayout.addWidget(self.tabWidget)

        # set central widget
        main_window.setCentralWidget(self.centralwidget)

