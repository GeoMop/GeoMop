# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import logging
import os
from shutil import copyfile
import shutil
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QDesktopServices

from communication import Communicator, Installation
from data.states import TaskStatus
from communication import installation
from threading import Timer
from ui.actions.main_menu_actions import *
from ui.data.config_builder import ConfigBuilder
from ui.data.mj_data import MultiJob, MultiJobActions
from ui.data.preset_data import Id
from ui.dialogs import AnalysisDialog, FilesSavedMessageBox, MessageDialog
from ui.dialogs.env_presets import EnvPresets
from ui.dialogs.multijob_dialog import MultiJobDialog
from ui.dialogs.options_dialog import OptionsDialog
from ui.dialogs.pbs_presets import PbsPresets
from ui.dialogs.resource_presets import ResourcePresets
from ui.dialogs.ssh_presets import SshPresets
from ui.req_scheduler import ReqScheduler
from ui.res_handler import ResHandler
from ui.menus.main_menu_bar import MainMenuBar
from ui.panels.overview import Overview
from ui.panels.tabs import Tabs

from geomop_project import Project, Analysis
import flow_util


logger = logging.getLogger("UiTrace")


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """
    multijobs_changed = QtCore.pyqtSignal(dict)


    @QtCore.pyqtSlot()
    def resume_paused_multijobs(self):
        for key, mj in self.data.multijobs.items():
            try:
                status = mj.get_state().status
                if status == TaskStatus.paused:
                    # create com worker
                    conf_builder = ConfigBuilder(self.data)
                    app_conf = conf_builder.build(key)
                    com = Communicator(app_conf)
                    self.com_manager.create_worker(key, com)

                    if status == TaskStatus.paused:
                        # resume
                        MultiJobActions.resuming(mj)
                        self.ui.overviewWidget.update_item(key, mj.get_state())
                        self.com_manager.resume(key)
            except Exception:
                pass
        self.resume_dialog.can_close = True
        self.resume_dialog.close()

    def __init__(self, parent=None, data=None, com_manager=None):
        super().__init__(parent)
        self.close_dialog = None
        # setup UI
        self.can_close = False
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

        self.res_handler.mj_installation.connect(
            self.handle_mj_installation)

        self.res_handler.mj_queued.connect(
            self.handle_mj_queued)

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

        self.analysis_dialog = None

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

        # project menu
        self.ui.menuBar.project.config = self.data.config

        # connect exit action
        self.ui.menuBar.app.actionExit.triggered.connect(
            QtWidgets.QApplication.quit)

        # connect exit action
        self.ui.menuBar.app.actionLog.triggered.connect(
            self._handle_log_action)

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

        # connect create analysis
        self.ui.menuBar.analysis.actionCreateAnalysis.triggered.connect(
            self._handle_create_analysis)

        # connect options
        self.ui.menuBar.settings.actionOptions.triggered.connect(
            self._handle_options)

        # connect current multijob changed
        self.ui.overviewWidget.currentItemChanged.connect(
            self.update_ui_locks)

        # connect tabWidget
        self.ui.tabWidget.ui.resultsTab.ui.saveButton.clicked.connect(
            self._handle_save_res_log_button_clicked)
        self.ui.tabWidget.ui.logsTab.ui.saveButton.clicked.connect(
            self._handle_save_res_log_button_clicked)

        # reload view
        self.ui.overviewWidget.reload_items(self.data.multijobs)

        # load settings
        self.load_settings()
        # attach workspace and project observers
        self.data.config.observers.append(Project)
        self.data.config.observers.append(self)

        # trigger notify
        self.data.config.notify()

        # resume paused multijobs

        self.resume_dialog = MessageDialog(self, MessageDialog.MESSAGE_ON_RESUME)
        self.resume_dialog.show()
        self.resume_dialog.activateWindow()
        # These solutions work, but prevent proper end of a process when mainwindow is closed.
        # Timer(0.5, lambda: QtCore.QMetaObject.invokeMethod(
        #     self, "resume_paused_multijobs", Qt.QueuedConnection)).start()
        QtCore.QTimer.singleShot(500, self.resume_paused_multijobs)
        # self.resume_paused_multijobs()

    def load_settings(self):
        # select last selected mj
        index = 0
        if self.data.config.selected_mj is not None:
            item_count = self.ui.overviewWidget.topLevelItemCount()
            tmp_index = int(self.data.config.selected_mj)
            if item_count > 0 and item_count > tmp_index:
                index = tmp_index
        item = self.ui.overviewWidget.topLevelItem(index)
        self.ui.overviewWidget.setCurrentItem(item)
        # load current project
        if self.data.config.project is not None:
            project = self.data.config.project
        else:
            project = '(No Project)'
        self.setWindowTitle('Jobs Scheduler - ' + project)

    def notify(self, data):
        """Handle update of data.set_data."""
        self.load_settings()
        # update analysis menu label - create / edit
        if Project.current is None or Project.current.get_current_analysis() is None:
            self.ui.menuBar.analysis.actionCreateAnalysis.setText('Create')
        else:
            self.ui.menuBar.analysis.actionCreateAnalysis.setText('Edit')

    def update_ui_locks(self, current, previous=None):
        if current is None:
            self.ui.menuBar.multiJob.lock_by_status(None)
        else:
            status = self.data.multijobs[current.text(0)].state.status
            self.ui.menuBar.multiJob.lock_by_status(status)
            mj = self.data.multijobs[current.text(0)]
            self.ui.tabWidget.reload_view(mj)

    @staticmethod
    def _handle_log_action():
        path = Installation.get_central_log_dir_static()
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    def _handle_add_multijob_action(self):
        self.mj_dlg.exec_add()

    def _handle_edit_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            preset = self.data.multijobs[key].get_preset()
            data = {
                "key": key,
                "preset": preset
            }
            self.mj_dlg.exec_edit(data)

    def _handle_copy_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            preset = copy.deepcopy(self.data.multijobs[key].get_preset())
            preset.name = self.mj_dlg.\
                PURPOSE_COPY_PREFIX + "_" + preset.name
            data = {
                "key": key,
                "preset": preset
            }
            self.mj_dlg.exec_copy(data)

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

        # sync mj analyses + files
        if Project.current is not None:
            mj_name = data["preset"].name
            mj_dir = Installation.get_config_dir_static(mj_name)
            proj_dir = Project.current.project_dir
            
            # get all files used by analyses
            files = []
            for analysis in Project.current.get_all_analyses():
                files.extend(analysis.files)

            analysis = Project.current.get_current_analysis()
            assert analysis is not None, "No analysis file exists for the project!"

            # copy the entire folder
            shutil.rmtree(mj_dir, ignore_errors=True)
            try:
                shutil.copytree(proj_dir, mj_dir)
            # Directories are the same
            except shutil.Error as e:
                logger.error("Failed to copy project dir: " + str(e))
            # Any error saying that the directory doesn't exist
            except OSError as e:
                logger.error("Failed to copy project dir: " + str(e))

            # fill in parameters and copy the files
            for file in set(files):
                src = os.path.join(proj_dir, file)
                dst = os.path.join(mj_dir, file)
                # create directory structure if not present
                dst_dir = os.path.dirname(dst)
                if not os.path.isdir(dst_dir):
                    os.makedirs(dst_dir)
                flow_util.analysis.replace_params_in_file(src, dst, analysis.params)

        self.multijobs_changed.emit(self.data.multijobs)

    def _handle_run_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        mj = self.data.multijobs[key]
        MultiJobActions.run(mj)

        self.ui.overviewWidget.update_item(key, mj.get_state())
        self.update_ui_locks(current)

        conf_builder = ConfigBuilder(self.data)
        app_conf = conf_builder.build(key)
        Communicator.lock_installation(app_conf)
        com = Communicator(app_conf)
        self.com_manager.install(key, com)
        Communicator.unlock_installation(com.mj_name)

        # reload tabs
        self.ui.tabWidget.reload_view(mj)

    def _handle_pause_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        mj = self.data.multijobs[key]
        MultiJobActions.pausing(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        self.update_ui_locks(current)

        self.com_manager.pause(key)

    def _handle_resume_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        mj = self.data.multijobs[key]
        MultiJobActions.resuming(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        self.update_ui_locks(current)

        self.com_manager.resume(key)

    def _handle_stop_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        mj = self.data.multijobs[key]
        MultiJobActions.stopping(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        self.update_ui_locks(current)

        self.com_manager.stop(key)
        Communicator.unlock_application(
            self.com_manager.get_communicator(key).mj_name)

    def _handle_create_analysis(self):
        # is project selected?
        if not Project.current:
            self.report_error("Project is not selected.")
            return

        # reload params
        Project.reload_current()

        # show new analysis dialog
        self.analysis_dialog = AnalysisDialog(self, Project.current)
        self.analysis_dialog.accepted.connect(self._handle_analysis_accepted)
        self.analysis_dialog.show()

    def _handle_analysis_accepted(self, purpose, data):
        if not Project.current:
            self.report_error("Project is not selected.")
            return
        if purpose in (AnalysisDialog.PURPOSE_ADD, AnalysisDialog.PURPOSE_EDIT):
            analysis = Analysis(**data)
            Project.current.save_analysis(analysis)

    def _handle_options(self):
        OptionsDialog(self, self.data.config).show()

    def handle_terminate(self):
        mj = self.data.multijobs
        for key in mj:
            state = mj[key].get_state()
            if state.get_status() == TaskStatus.running:
                state.set_status(TaskStatus.none)
        self.com_manager.terminate()

        # save currently selected mj
        current = self.ui.overviewWidget.currentItem()
        sel_index = self.ui.overviewWidget.indexOfTopLevelItem(current)
        self.data.config.selected_mj = sel_index

    def _handle_restart_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        mj = self.data.multijobs[key]
        MultiJobActions.stopping(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        self.update_ui_locks(current)
        self.com_manager.restart(key)

    def handle_mj_installed(self, key):
        mj = self.data.multijobs[key]
        MultiJobActions.running(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_installation(self, key):
        mj = self.data.multijobs[key]
        MultiJobActions.installation(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_queued(self, key):
        mj = self.data.multijobs[key]
        MultiJobActions.queued(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_paused(self, key):
        mj = self.data.multijobs[key]
        MultiJobActions.paused(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_resumed(self, key):
        mj = self.data.multijobs[key]
        MultiJobActions.resumed(mj)
        self.ui.overviewWidget.update_item(key, mj.get_state())

        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_stopped(self, key):
        mj = self.data.multijobs[key]
        if mj.state.status is not TaskStatus.finished:
            MultiJobActions.stopped(mj)
            self.ui.overviewWidget.update_item(key, mj.get_state())
        current = self.ui.overviewWidget.currentItem()
        self.update_ui_locks(current)

    def handle_mj_state(self, key, state):
        mj = self.data.multijobs[key]
        if state.status == TaskStatus.running:
            mj.get_state().update(state)
            self.ui.overviewWidget.update_item(key, mj.get_state())
        elif state.status == TaskStatus.ready:
            mj.get_state().update(state)
            MultiJobActions.finished(mj)
            self.ui.overviewWidget.update_item(key, mj.get_state())

            current = self.ui.overviewWidget.currentItem()
            self.update_ui_locks(current)
            self.com_manager.finish(key)
            Communicator.unlock_application(
                self.com_manager.get_communicator(key).mj_name)

    def handle_mj_result(self, key):
        mj = self.data.multijobs[key]
        current = self.ui.overviewWidget.currentItem()
        if current.text(0) == key:
            self.ui.tabWidget.reload_view(mj)

    def _handle_save_results_button_clicked(self):
        src_dir_path = os.path.join(installation.__install_dir__,
                                    installation.__jobs_dir__,
                                    self.current_mj.preset.name,
                                    installation.__result_dir__)
        dst_dir_name = installation.__result_dir__
        files = self.ui.tabWidget.ui.resultsTab.files
        self._handle_save_results(src_dir_path, dst_dir_name, files)

    def _handle_save_res_log_button_clicked(self):
        # if not project - alert
        if not Project.current:
            self.report_error("No project selected!")

        dst_dir_location = os.path.join(Project.current.project_dir,
                                        "analysis",
                                        time.strftime("%Y%m%d_%H%M%S"))
        self._save_results(dst_dir_location)
        self._save_logs(dst_dir_location)
        # alert with open dir option
        FilesSavedMessageBox(self, dst_dir_location).show()

    def _save_logs(self, dst_dir_location):
        src_dir_path = os.path.join(installation.__install_dir__,
                                    installation.__jobs_dir__,
                                    self.current_mj.preset.name,
                                    installation.__result_dir__,
                                    installation.__logs_dir__)
        dst_dir_path = os.path.join(dst_dir_location,
                                    installation.__logs_dir__)
        files = self.ui.tabWidget.ui.logsTab.files
        self.copy_files(src_dir_path, dst_dir_path, files)

    def _save_results(self, dst_dir_location):
        src_dir_path = os.path.join(installation.__install_dir__,
                                    installation.__jobs_dir__,
                                    self.current_mj.preset.name,
                                    installation.__result_dir__)
        dst_dir_path = os.path.join(dst_dir_location,
                                    installation.__result_dir__)
        files = self.ui.tabWidget.ui.resultsTab.files
        self.copy_files(src_dir_path, dst_dir_path, files)

    @staticmethod
    def copy_files(src_dir_path, dst_dir_path, files):
        # create folder
        os.makedirs(dst_dir_path, exist_ok=True)

        # copy files
        for file_name in [f.file_name for f in files]:
            copyfile(os.path.join(src_dir_path, file_name), os.path.join(dst_dir_path, file_name))

    def report_error(self, msg, err=None):
        """Report an error with dialog."""
        from geomop_dialogs import GMErrorDialog
        err_dialog = GMErrorDialog(self)
        err_dialog.open_error_dialog(msg, err)

    @property
    def current_mj(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        mj = self.data.multijobs[key]
        return mj

    def showEvent(self, event):
        super(MainWindow, self).showEvent(event)
        self.raise_()

        # select workspace if none is selected
        if self.data.config.workspace is None:
            import sys
            sel_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose workspace")
            if not sel_dir:
                sel_dir = None
            elif sys.platform == "win32":
                sel_dir = sel_dir.replace('/', '\\')
            self.data.config.workspace = sel_dir
            self.data.config.save()

    def closeEvent(self, event):
        if self.can_close:
            event.accept()
            return

        def check_if_all_mj_paused():
            all_paused = True
            for key, mj in self.data.multijobs.items():
                status = mj.get_state().status
                if status in (TaskStatus.installation, TaskStatus.resuming, TaskStatus.pausing):
                    # wait for finish
                    all_paused = False
                elif status == TaskStatus.running:
                    # pause mj
                    MultiJobActions.pausing(mj)
                    self.ui.overviewWidget.update_item(key, mj.get_state())
                    self.com_manager.pause(key)
                    all_paused = False

            if not all_paused:
                Timer(1, check_if_all_mj_paused).start()
                return False

            if self.close_dialog:
                self.close_dialog.can_close = True
                self.close_dialog.close()
            self.can_close = True
            self.close()
            return True

        if not check_if_all_mj_paused():
            self.close_dialog = MessageDialog(self, MessageDialog.MESSAGE_ON_EXIT)
            self.close_dialog.show()
            self.close_dialog.activateWindow()
            event.ignore()
        else:
            event.accept()


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
