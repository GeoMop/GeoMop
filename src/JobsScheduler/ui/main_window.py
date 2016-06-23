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
import time

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from communication import Installation
from data.states import TaskStatus, TASK_STATUS_STARTUP_ACTIONS, MultijobActions
from communication import installation
from ui.actions.main_menu_actions import *
from ui.data.mj_data import MultiJob, AMultiJobFile
from ui.data.preset_data import Id
from ui.dialogs import AnalysisDialog, FilesSavedMessageBox, MessageDialog
from ui.dialogs.env_presets import EnvPresets
from ui.dialogs.multijob_dialog import MultiJobDialog
from ui.dialogs.options_dialog import OptionsDialog
from ui.dialogs.pbs_presets import PbsPresets
from ui.dialogs.resource_presets import ResourcePresets
from ui.dialogs.ssh_presets import SshPresets
from ui.menus.main_menu_bar import MainMenuBar
from ui.panels.overview import Overview
from ui.panels.tabs import Tabs

from geomop_project import Project, Analysis


logger = logging.getLogger("UiTrace")


class MainWindow(QtWidgets.QMainWindow):
    """
    Jobs Scheduler main window class
    """

    DEFAULT_POLL_INTERVAL = 500
    """default polling interval in ms"""

    multijobs_changed = QtCore.pyqtSignal(dict)

    def perform_multijob_startup_action(self):
        for mj_id, mj in self.data.multijobs.items():
            status = mj.get_state().status
            action = TASK_STATUS_STARTUP_ACTIONS[status]
            if action == MultijobActions.resume:
                self.com_manager.resume_jobs.append(mj_id)
            elif action == MultijobActions.terminate:
                self.com_manager.terminate_jobs.append(mj_id)

    def __init__(self, parent=None, data=None, com_manager=None):
        super().__init__(parent)
        self.close_dialog = None
        # setup UI
        self.closing = False
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)
        self.data = data

        # Com Manager related
        self.com_manager = com_manager

        self.cm_poll_interval = MainWindow.DEFAULT_POLL_INTERVAL
        """current com manager polling interval in ms"""

        self.cm_poll_timer = QtCore.QTimer()
        self.cm_poll_timer.timeout.connect(self.poll_com_manager)
        self.cm_poll_timer.start(self.cm_poll_interval)

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
        self.ui.menuBar.multiJob.actionReuseMultiJob.triggered.connect(
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
        self.ui.menuBar.multiJob.actionStopMultiJob.triggered.connect(
            self._handle_stop_multijob_action)

        # connect create analysis
        self.ui.menuBar.analysis.actionCreateAnalysis.triggered.connect(
            self._handle_create_analysis)

        # connect options
        self.ui.menuBar.settings.actionOptions.triggered.connect(
            self._handle_options)

        # connect current multijob changed
        self.ui.overviewWidget.currentItemChanged.connect(
            self._handle_current_mj_changed)

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
        self.perform_multijob_startup_action()

    def poll_com_manager(self):
        """poll com manager and update gui"""
        self.com_manager.poll()

        current = self.ui.overviewWidget.currentItem()
        current_mj_id = current.text(0)

        for mj_id in self.com_manager.state_change_jobs:
            mj = self.data.multijobs[mj_id]
            self.ui.overviewWidget.update_item(mj_id, mj.get_state())
            if current_mj_id == mj_id:
                self.update_ui_locks(mj_id)

        overview_change_jobs = set(self.com_manager.results_change_jobs)
        overview_change_jobs.update(self.com_manager.jobs_change_jobs)
        overview_change_jobs.update(self.com_manager.logs_change_jobs)

        for mj_id in overview_change_jobs:
            if current_mj_id == mj_id:
                mj = self.data.multijobs[mj_id]
                self.ui.tabWidget.reload_view(mj)

        self.com_manager.state_change_jobs = []
        self.com_manager.results_change_jobs = []
        self.com_manager.jobs_change_jobs = []
        self.com_manager.logs_change_jobs = []

        # close application
        if self.closing and not self.com_manager.run_jobs and not self.com_manager.start_jobs:
            self.close()

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

    def update_ui_locks(self, mj_id):
        if mj_id is None:
            self.ui.menuBar.multiJob.lock_by_status(None)
        else:
            status = self.data.multijobs[mj_id].state.status
            self.ui.menuBar.multiJob.lock_by_status(status)
            mj = self.data.multijobs[mj_id]
            self.ui.tabWidget.reload_view(mj)

    def _handle_current_mj_changed(self, current, previous=None):
        if current is not None:
            mj_id = current.text(0)
        else:
            mj_id = None
        self.update_ui_locks(mj_id)

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
        self.multijobs_changed.emit(self.data.multijobs)

    def _handle_run_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        self.com_manager.start_jobs.append(key)

    def _handle_resume_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        self.com_manager.resume_jobs.append(key)

    def _handle_stop_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        self.com_manager.stop_jobs.append(key)

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
                                        "analysis_results",
                                        time.strftime("%Y%m%d_%H%M%S"))
        self._save_results(dst_dir_location)
        self._save_logs(dst_dir_location)
        self._save_debug_files(dst_dir_location)

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

    def _save_debug_files(self, dst_dir_location):
        """Save file usefull for debug (That will send to developer)"""
        app = os.path.join(os.path.split(
            os.path.dirname(os.path.realpath(__file__)))[0])        
        res_dir_path = os.path.join(installation.__install_dir__,
                                    installation.__jobs_dir__,
                                    self.current_mj.preset.name)
        conf_dir_path = os.path.join(res_dir_path, installation.__conf_dir__)
        dst_dir_path = os.path.join(dst_dir_location,
                                    installation.__conf_dir__)
        central_log_file = []
        central_log_file.append(AMultiJobFile(
            os.path.join(app, "log"), "app-centrall.log"))
        self.copy_files(app, os.path.join(
            dst_dir_location, "log"), central_log_file)

        files = self._get_config_files(conf_dir_path)
        self.copy_files(conf_dir_path, dst_dir_path, files)

    @staticmethod
    def _get_config_files(conf_dir_path):
        """get all files in conf directory"""
        conf_files = []
        for root, dirs, files in os.walk(conf_dir_path):
            for name in files:
                conf_files.append(AMultiJobFile(root, name))
        return conf_files

    @staticmethod
    def copy_files(src_dir_path, dst_dir_path, files):
        """copy results files to workspace folder"""
        os.makedirs(dst_dir_path, exist_ok=True)
        for f in files:
            file_name = os.path.basename(f.file_path)
            res_dir = os.path.dirname(os.path.abspath(f.file_path))
            if os.path.samefile(src_dir_path, res_dir):
                copyfile(f.file_path, os.path.join(dst_dir_path, file_name))
            else:            
                ext_path = dst_dir_path
                res_dir, tail = os.path.split(res_dir)
                while len(res_dir)>0:
                    ext_path = os.path.join(ext_path, tail)
                    if os.path.samefile(src_dir_path, res_dir):
                        os.makedirs(ext_path, exist_ok=True)
                        copyfile(f.file_path, 
                             os.path.join(ext_path, file_name))
                        break
                    res_dir, tail = os.path.split(res_dir)

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
        if not self.closing:
            self.closing = True

            # save currently selected mj
            current = self.ui.overviewWidget.currentItem()
            sel_index = self.ui.overviewWidget.indexOfTopLevelItem(current)
            self.data.config.selected_mj = sel_index

            # pause all jobs
            self.com_manager.pause_all()
            self.cm_poll_interval = 200
            self.cm_poll_timer.stop()
            self.cm_poll_timer.start(self.cm_poll_interval)

            # show closing dialog
            self.close_dialog = MessageDialog(self, MessageDialog.MESSAGE_ON_EXIT)
            self.close_dialog.show()
            self.close_dialog.activateWindow()

            event.ignore()

        elif not self.com_manager.run_jobs and not self.com_manager.start_jobs:
            # all jobs have been paused, close window
            if self.close_dialog:
                self.close_dialog.can_close = True
                self.close_dialog.close()

            # save data
            self.data.save_all()

            event.accept()
        else:
            event.ignore()


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
