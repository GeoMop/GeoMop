# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import logging
import os
import time
import shutil
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from ..communication import installation
from ..data.states import TaskStatus, TASK_STATUS_STARTUP_ACTIONS, MultijobActions
from ..ui.actions.main_menu_actions import *
from ..ui.data.mj_data import MultiJob, AMultiJobFile
from ..ui.imports.workspaces_conf import BASE_DIR
from ..ui.dialogs import MessageDialog
from ..ui.dialogs.env_presets import EnvPresets
from ..ui.dialogs.multijob_dialog import MultiJobDialog
from ..ui.dialogs.options_dialog import OptionsDialog
from ..ui.dialogs.pbs_presets import PbsPresets
from ..ui.dialogs.resource_presets import ResourcePresets
from ..ui.dialogs.ssh_presets import SshPresets
from ..ui.menus.main_menu_bar import MainMenuBar
from ..ui.panels.overview import Overview
from ..ui.panels.tabs import Tabs

from gm_base.geomop_analysis import Analysis, MULTIJOBS_DIR
from gm_base.config import __config_dir__


logger = logging.getLogger("UiTrace")


LOG_PATH = os.path.join(__config_dir__, BASE_DIR,'log', 'app-centrall.log')


class MainWindow(QtWidgets.QMainWindow):
    """
    Job Panel main window class
    """

    DEFAULT_POLL_INTERVAL = 100
    """default polling interval in ms"""

    multijobs_changed = QtCore.pyqtSignal(dict)
    
    def perform_reload_action(self):
        # reload view
        self.ui.overviewWidget.reload_items(self.data.multijobs)
        for mj_id, mj in self.data.multijobs.items():
            status = mj.get_state().status
            if status == TaskStatus.deleting:
                if mj.last_status is not None:
                    mj.get_state().status = mj.last_status
                    mj.last_status = None
                else:
                    mj.get_state().status = TaskStatus.error
                    self.error = "Multijob data is corrupted"
            action = TASK_STATUS_STARTUP_ACTIONS[status]
            if action == MultijobActions.resume:
                #self.frontend_service._resume_jobs.append(mj_id)
                pass
            elif action == MultijobActions.terminate:
                #self.frontend_service._terminate_jobs.append(mj_id)
                pass

    def __init__(self, parent=None, data=None, frontend_service=None):
        super().__init__(parent)
        self.__pool_lock = threading.Lock()
        """lock for prevention of pool multiple runnig"""
        self.close_dialog = None
        # setup UI
        self.closing = False
        self.ui = UiMainWindow()
        self.ui.setup_ui(self)
        self.data = data

        # Com Manager related
        self.frontend_service = frontend_service

        self.cm_poll_interval = MainWindow.DEFAULT_POLL_INTERVAL
        """current com manager polling interval in ms"""

        self.cm_poll_timer = QtCore.QTimer()
        self.cm_poll_timer.timeout.connect(self.poll_com_manager)
        self.cm_poll_timer.start(self.cm_poll_interval)

        self._delete_mj_local = []

        # multijob dialog
        self.ui.menuBar.multiJob.actionAddMultiJob.triggered.connect(
            self._handle_add_multijob_action)
        self.ui.menuBar.multiJob.actionReuseMultiJob.triggered.connect(
            self._handle_reuse_multijob_action)
        self.ui.menuBar.multiJob.actionDeleteMultiJob.triggered.connect(
            self._handle_delete_multijob_action)
        self.ui.menuBar.multiJob.actionSendReport.triggered.connect(
            self._handle_send_report_action)
        self.ui.menuBar.multiJob.actionDeleteRemote.triggered.connect(
            self._handle_delete_remote_action)
        self.ui.menuBar.multiJob.actionDownloadWholeMultiJob.triggered.connect(
            self._handle_download_whole_multijob_action)
        self.multijobs_changed.connect(self.ui.overviewWidget.reload_items)
        self.multijobs_changed.connect(self.data.save_mj)
        # ssh presets
        self.ui.menuBar.settings.actionSshPresets.triggered.connect(self.set_ssh)
        # pbs presets
        self.ui.menuBar.settings.actionPbsPresets.triggered.connect(self.set_pbs)
        # env presets
        self.ui.menuBar.settings.actionEnvPresets.triggered.connect(self.set_env)
        # resource presets
        self.ui.menuBar.settings.actionResourcesPresets.triggered.connect(self.set_res)

        # analysis menu
        self.ui.menuBar.analysis.config = self.data.workspaces
        
        # connect exit action
        self.ui.menuBar.app.actionExit.triggered.connect(
            QtWidgets.QApplication.quit)

        # connect log action
        self.ui.menuBar.app.actionLog.triggered.connect(
            self._handle_log_action)

        # connect remove log action
        self.ui.menuBar.app.actionRemLog.triggered.connect(
            self._handle_rem_log_action)

        # connect multijob stop action
        self.ui.menuBar.multiJob.actionStopMultiJob.triggered.connect(
            self._handle_stop_multijob_action)

        # connect options
        self.ui.menuBar.settings.actionOptions.triggered.connect(
            self._handle_options)

        # connect current multijob changed
        self.ui.overviewWidget.currentItemChanged.connect(
            self._handle_current_mj_changed)

        # load settings
        self.load_settings()
        # attach workspace and project observers
        self.data.config.observers.append(self)

        # trigger notify
        self.data.config.notify()
        
        #reload func
        self.data.set_reload_funcs(self.pause_all, self.perform_reload_action)

        # resume paused multijobs
        self.perform_reload_action()

        self.setWindowTitle('Jobs Panel')

    def poll_com_manager(self):
        """poll com manager and update gui"""
        if not self.__pool_lock.acquire(False):
            return
        self.frontend_service.run_body()

        current = self.ui.overviewWidget.currentItem()
        if current is not None:
            current_mj_id = current.text(0)

        state_change_jobs = self.frontend_service.get_mj_changed_state()
        for mj_id in state_change_jobs:
            mj = self.data.multijobs[mj_id]
            self.ui.overviewWidget.update_item(mj_id, mj.get_state())
            if current_mj_id == mj_id:
                self.update_ui_locks(mj_id)

            # if mj.state.status == TaskStatus.finished:
            #     # copy app central log into mj
            #     mj_dir = os.path.join(self.data.workspaces.get_path(), mj.preset.analysis,
            #                           MULTIJOBS_DIR, mj.preset.name)
            #     shutil.copy(LOG_PATH, mj_dir)

                # check if all jobs finished successfully for a finished multijob
                for job in mj.get_jobs():
                    if job.status == TaskStatus.error:
                        mj.state.status = TaskStatus.error
                        mj.error = "Not all jobs finished successfully."
                        self.multijobs_changed.emit(self.data.multijobs)
                        break

        for mj_id in state_change_jobs:
            if current_mj_id == mj_id:
                mj = self.data.multijobs[mj_id]
                self.ui.tabWidget.reload_view(mj)

        for mj_id, error in self.frontend_service._jobs_deleted.items():
            mj = self.data.multijobs[mj_id]
            if error is None:
                if mj_id in self._delete_mj_local:
                    mj_dir = os.path.join(self.data.workspaces.get_path(), mj.preset.analysis,
                                          MULTIJOBS_DIR, mj.preset.name)
                    shutil.rmtree(mj_dir)
                    self.data.multijobs.pop(mj_id)  # delete from gui
                else:
                    self.data.multijobs[mj_id].preset.deleted_remote = True
            else:
                self.report_error("Deleting error: {0}".format(error))
            mj.get_state().status = mj.last_status
            mj.last_status = None
        
        if len(self.frontend_service._jobs_deleted)>0:
            self.multijobs_changed.emit(self.data.multijobs)

        self.frontend_service._jobs_deleted = {}

        # close application
        if self.closing and not self.frontend_service._run_jobs and not self.frontend_service._start_jobs \
                and not self.frontend_service._delete_jobs:
            self.close()
        self.__pool_lock.release()
        
    def set_ssh(self):                                 
        """ssh dialog"""
        ssh_dlg = SshPresets(parent=self,
                             presets=self.data.ssh_presets,
                             container=self.data,
                             frontend_service=self.frontend_service)
        ssh_dlg.exec_()
                                          
    def set_pbs(self):                                 
        """pbs dialog"""
        pbs_dlg = PbsPresets(parent=self,
                                          presets=self.data.pbs_presets)
        pbs_dlg.exec_()
                                          
    def set_res(self):                                 
        """resource dialog"""                                      
        res_dlg = ResourcePresets(parent=self,
                              presets=self.data.resource_presets,
                              pbs=self.data.pbs_presets,
                              ssh=self.data.ssh_presets)
        res_dlg.exec_()

    def set_env(self):                                 
        """Environment dialog"""
        env_dlg = EnvPresets(parent=self,
                                          presets=self.data.env_presets)
        env_dlg.exec_()

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

    def notify(self):
        """Handle update of data.set_data."""
        self.load_settings()
        class ConfigI:
            def __init__(self, workspace, analysis):
                self.workspace = workspace
                self.analysis = analysis  
        Analysis.notify(ConfigI( self.data.workspaces.get_path(), self.data.config.analysis))

    def update_ui_locks(self, mj_id):
        if mj_id is None:
            self.ui.menuBar.multiJob.lock_by_status(True, None)
            self.ui.tabWidget.reload_view(None)
        else:
            status = self.data.multijobs[mj_id].state.status
            rdeleted = self.data.multijobs[mj_id].preset.deleted_remote
            self.ui.menuBar.multiJob.lock_by_status(rdeleted, status)
            mj = self.data.multijobs[mj_id]
            self.ui.tabWidget.reload_view(mj)

    def _handle_current_mj_changed(self, current, previous=None):
        if current is not None:
            mj_id = current.text(0)
            mj = self.data.multijobs[mj_id]

            # show error message in status bar
            self.ui.status_bar.showMessage(mj.error)
        else:
            mj_id = None
        self.update_ui_locks(mj_id)

    @staticmethod
    def _handle_log_action():
        path = installation.Installation.get_central_log_dir_static()
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

    @staticmethod
    def _handle_rem_log_action():
        path = installation.Installation.get_central_log_dir_static()
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                with open(file_path, 'w'):
                    pass
                    
    def _handle_add_multijob_action(self):
        mj_dlg = MultiJobDialog(parent=self, data=self.data)
        ret = mj_dlg.exec_add()
        if ret==QtWidgets.QDialog.Accepted:
            self.handle_multijob_dialog(mj_dlg.purpose, mj_dlg.get_data())

    def _handle_reuse_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            preset = copy.deepcopy(self.data.multijobs[key].get_preset())
            preset.from_mj = key
            data = {
                "key": key,
                "preset": preset
            }

            mj_dlg = MultiJobDialog(parent=self, data=self.data)
            ret = mj_dlg.exec_copy(data)
            if ret==QtWidgets.QDialog.Accepted:
                self.handle_multijob_dialog(mj_dlg.purpose, mj_dlg.get_data())

    def _handle_delete_multijob_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            if self.data.multijobs[key].preset.deleted_remote:
                self.frontend_service._jobs_deleted[key] = None
                self._delete_mj_local.append(key)
            else:
                self.frontend_service.mj_delete(key)
                self._delete_mj_local.append(key)
            self._set_deleting(key)
            
    def _handle_send_report_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            mj = self.data.multijobs[key]
            mj_name = mj.preset.name
            an_name = mj.preset.analysis
            dialog = QtWidgets.QFileDialog(
                self, "Choose Multijob Report File Name",
                os.path.join(self.data.config.report_dir, key + ".zip"), 
                "Report Archiv Files (*.zip)")
            dialog.setDefaultSuffix('.zip')
            dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
            dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            dialog.setViewMode(QtWidgets.QFileDialog.Detail)
            if dialog.exec_():                
                report_file = dialog.selectedFiles()[0]
                dir = dialog.directory().absolutePath()
                if dir:
                    self.data.config.report_dir = dir
                    self.data.config.save()
                if report_file:
                    central_log_path = installation.Installation.get_central_log_dir_static()
                    log_path = installation.Installation.get_mj_log_dir_static(mj_name, an_name)
                    config_path = installation.Installation.get_config_dir_static(mj_name, an_name)
                    tmp_dir = os.path.join(__config_dir__, BASE_DIR, "tmp")
                    output_dir = os.path.join(__config_dir__, BASE_DIR, "tmp", "output_zip")
                    if not os.path.isdir(tmp_dir):
                        os.makedirs(tmp_dir)
                    if os.path.isdir(output_dir):
                        shutil.rmtree(output_dir, ignore_errors=True)
                    os.makedirs(output_dir)
                    if os.path.isdir(output_dir):
                        shutil.copytree(central_log_path, os.path.join(output_dir, "central"))
                    if os.path.isdir(config_path):
                        shutil.copytree(config_path, os.path.join(output_dir, "config"))
                    if os.path.isdir(log_path):
                        shutil.copytree(log_path, os.path.join(output_dir,"log" ))
                    shutil.make_archive(report_file,"zip", output_dir)
                    shutil.rmtree(output_dir, ignore_errors=True)
            
    def _set_deleting(self, key):
        """save state before deleting and mark mj as deleted"""
        mj = self.data.multijobs[key]        
        if mj.get_state().status == TaskStatus.deleting:
            return
        mj.last_status = mj.get_state().status
        mj.get_state().status = TaskStatus.deleting
        self.ui.overviewWidget.update_item(key, mj.get_state())

    def _handle_delete_remote_action(self):
        if self.data.multijobs:
            key = self.ui.overviewWidget.currentItem().text(0)
            if not self.data.multijobs[key].preset.deleted_remote:
                self.frontend_service.mj_delete(key)
                self._set_deleting(key)

    def _handle_download_whole_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        self.frontend_service.download_whole_mj(key)

    def handle_multijob_dialog(self, purpose, data):
        mj = MultiJob(data['preset'])
        if purpose in (MultiJobDialog.PURPOSE_ADD, MultiJobDialog.PURPOSE_COPY):
            mj.state.analysis = mj.preset.analysis
            try:
                analysis = Analysis.open(self.data.workspaces.get_path(), mj.preset.analysis)
            except Exception as e:
                self.report_error("Multijob error", e)
                self.multijobs_changed.emit(self.data.multijobs)
                return
            analysis.mj_counter += 1
            analysis.save()
            if purpose == MultiJobDialog.PURPOSE_ADD:
                # Create multijob folder and copy analysis into it
                try:
                    analysis.copy_into_mj_folder(mj)
                except Exception as e:
                    logger.error("Failed to copy analysis into mj folder: " + str(e))                
                self.data.multijobs[mj.id] = mj
                self.frontend_service.mj_start(mj.id)
            elif purpose == MultiJobDialog.PURPOSE_COPY:
                self.data.multijobs[mj.id] = mj
                src_mj_name = self.data.multijobs[mj.preset.from_mj].preset.name
                src_dir = os.path.join(self.data.workspaces.get_path(), mj.preset.analysis,
                                       MULTIJOBS_DIR, src_mj_name)
                dst_dir = os.path.join(self.data.workspaces.get_path(), mj.preset.analysis,
                                       MULTIJOBS_DIR, mj.preset.name)
                shutil.copytree(src_dir, dst_dir, ignore=shutil.ignore_patterns(
                    'res', 'log', 'status', 'mj_conf', '*.log'))                
                self.frontend_service.mj_start(mj.id)
        self.multijobs_changed.emit(self.data.multijobs)

    def _handle_resume_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        #self.frontend_service._resume_jobs.append(key)

    def _handle_stop_multijob_action(self):
        current = self.ui.overviewWidget.currentItem()
        key = current.text(0)
        self.frontend_service.mj_stop(key)

    def _handle_options(self):
        OptionsDialog(self, self.data,self.data.env_presets).show()

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
                shutil.copyfile(f.file_path, os.path.join(dst_dir_path, file_name))
            else:            
                ext_path = dst_dir_path
                res_dir, tail = os.path.split(res_dir)
                while len(res_dir)>0:
                    ext_path = os.path.join(ext_path, tail)
                    if os.path.samefile(src_dir_path, res_dir):
                        os.makedirs(ext_path, exist_ok=True)
                        shutil.copyfile(f.file_path, 
                             os.path.join(ext_path, file_name))
                        break
                    res_dir, tail = os.path.split(res_dir)

    def report_error(self, msg, err=None):
        """Report an error with dialog."""
        from gm_base.geomop_dialogs import GMErrorDialog
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

        return
        # select workspace if none is selected
        if self.data.workspaces.get_path() is None:
            import sys
            sel_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose workspace")
            if not sel_dir:
                sel_dir = None
            elif sys.platform == "win32":
                sel_dir = sel_dir.replace('/', '\\')
            self.data.reload_workspace(sel_dir)

    def pause_all(self):        
        # save currently selected mj
        current = self.ui.overviewWidget.currentItem()
        sel_index = self.ui.overviewWidget.indexOfTopLevelItem(current)
        self.data.config.selected_mj = sel_index

        # pause all jobs
        self.frontend_service.pause_all()
        self.cm_poll_timer.stop()
        self.cm_poll_timer.start(self.cm_poll_interval)
        
        while self.frontend_service._run_jobs or self.frontend_service._start_jobs or \
            self.frontend_service._delete_jobs:
            self.poll_com_manager()
            time.sleep(200)

    def closeEvent(self, event):
        if not self.closing:
            self.closing = True

            # save currently selected mj
            current = self.ui.overviewWidget.currentItem()
            sel_index = self.ui.overviewWidget.indexOfTopLevelItem(current)
            self.data.config.selected_mj = sel_index

            # pause all jobs
            self.frontend_service.pause_all()
            self.cm_poll_interval = 200
            self.cm_poll_timer.stop()
            self.cm_poll_timer.start(self.cm_poll_interval)
            
            i=0
            while (self.frontend_service._run_jobs or self.frontend_service._start_jobs or \
                self.frontend_service._delete_jobs) and i<3:
                self.poll_com_manager()
                time.sleep(200)
                i += 1

            if self.frontend_service._run_jobs or self.frontend_service._start_jobs or \
                self.frontend_service._delete_jobs:
                # show closing dialog
                self.close_dialog = MessageDialog(self, MessageDialog.MESSAGE_ON_EXIT)
                self.close_dialog.show()
                self.close_dialog.activateWindow()

            event.ignore()

        elif not self.frontend_service._run_jobs and not self.frontend_service._start_jobs:
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
    Jobs Panel UI
    """
    def setup_ui(self, main_window):
        """
        Setup basic UI
        """
        # main window
        main_window.resize(1154, 702)
        main_window.setObjectName("MainWindow")
        main_window.setWindowTitle('Job Panel')

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

        # status bar
        self.status_bar = main_window.statusBar()
