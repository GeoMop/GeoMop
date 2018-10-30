# -*- coding: utf-8 -*-
"""
Main window menus
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets
import JobPanel.ui.actions.main_menu_actions as action
from JobPanel.data.states import TaskStatus, MultijobActions, TASK_STATUS_PERMITTED_ACTIONS
from JobPanel.ui.menus import AnalysisMenu


class MainMenuBar(QtWidgets.QMenuBar):
    """
    Main windows menu bar.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainMenuBar")

        # menus
        self.app = AppMenu(self)
        self.multiJob = MultiJobMenu(self)
        self.settings = SettingsMenu(self)
        self.analysis = AnalysisMenu(self, {})

        # add menus to main menu
        self.addAction(self.app.menuAction())
        self.addAction(self.multiJob.menuAction())
        self.addAction(self.analysis.menuAction())
        self.addAction(self.settings.menuAction())


class AppMenu(QtWidgets.QMenu):
    """
    App sub menu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Menu")
        self.setObjectName("appMenu")

        # app actions
        self.actionExit = action.ActionExit(self)
        self.actionLog = action.ActionLog(self)
        self.actionRemLog = action.ActionRemLog(self)

        # add actions to menu
        self.addAction(self.actionExit)
        self.addAction(self.actionLog)
        self.addAction(self.actionRemLog)


class MultiJobMenu(QtWidgets.QMenu):
    """
    MultiJob sub menu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("MultiJob")
        self.setObjectName("multiJobMenu")

        # creating actions
        self.actionAddMultiJob = action.ActionAddMultiJob(self)
        self.actionReuseMultiJob = action.ActionReuseMultiJob(self)
        self.actionDeleteRemote = action.ActionDeleteRemote(self)
        self.actionDeleteMultiJob = action.ActionDeleteMultiJob(self)

        # control actions
        self.actionStopMultiJob = action.ActionStopMultiJob(self)
        self.actionSendReport = action.ActionSendReport(self)

        self.actionDownloadWholeMultiJob = action.ActionDownloadWholeMultiJob(self)

        # add actions to menu
        self.addAction(self.actionAddMultiJob)
        self.addAction(self.actionReuseMultiJob)
        self.addAction(self.actionDeleteRemote)
        self.addAction(self.actionDeleteMultiJob)
        self.addSeparator()
        self.addAction(self.actionStopMultiJob)
        self.addAction(self.actionSendReport) 
        self.addSeparator()
        self.addAction(self.actionDownloadWholeMultiJob)

        self.lockable_actions = {
            MultijobActions.reuse: self.actionReuseMultiJob,
            MultijobActions.delete_remote:  self.actionDeleteRemote,
            MultijobActions.delete: self.actionDeleteMultiJob,
            MultijobActions.stop: self.actionStopMultiJob,
            MultijobActions.send_report: self.actionSendReport,
            MultijobActions.download_whole: self.actionDownloadWholeMultiJob
        }
        
        self.rdeleted_actions = {
            MultijobActions.delete_remote:  self.actionDeleteRemote,
            MultijobActions.download_whole: self.actionDownloadWholeMultiJob
        }

        self.downloaded_actions = {
            MultijobActions.download_whole: self.actionDownloadWholeMultiJob
        }

        self.lock_by_status(True, True, True)

    def lock_by_status(self, rdeleted, downloaded, mj_local, task_status=None):
        """
        Locks UI actions based on selected MultiJob. Status None means no MultiJob.
        :param task_status: Status that controls the locks.
        :return:
        """
        for mj_action, menu_action in self.lockable_actions.items():
            if task_status is None or \
                    (task_status, mj_action) not in TASK_STATUS_PERMITTED_ACTIONS or \
                    (mj_action in self.rdeleted_actions and rdeleted) or \
                    (mj_action in self.downloaded_actions and downloaded) or \
                    (mj_action == MultijobActions.reuse and not mj_local and rdeleted) or \
                    (mj_action == MultijobActions.download_whole and mj_local):
                menu_action.setDisabled(True)
            else:
                menu_action.setDisabled(False)

    def lock_for_selection(self, rdeleted, statuses):
        """
		Locks UI actions based on selected MultiJobs.
		Disables actions in UI which don't make sense.
		:param statuses: statuses of selected MJ
		"""
        self.actionDownloadWholeMultiJob.setDisabled(True)
        self.actionReuseMultiJob.setDisabled(True)
        self.actionSendReport.setDisabled(True)
        self.actionDeleteRemote.setDisabled(rdeleted)
        deleted = True
        for status in statuses:
            if (status, MultijobActions.delete) in TASK_STATUS_PERMITTED_ACTIONS:
                deleted = False
        self.actionDeleteMultiJob.setDisabled(deleted)
        stopped = True
        for status in statuses:
            if (status, MultijobActions.stop) in TASK_STATUS_PERMITTED_ACTIONS:
                stopped = False
        self.actionStopMultiJob.setDisabled(stopped)




class SettingsMenu(QtWidgets.QMenu):
    """
    Settings sub menu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Settings")
        self.setObjectName("settingsMenu")

        # preset actions
        self.actionSshPresets = action.ActionSshPresets(self)
        self.actionEnvPresets = action.ActionEnvPresets(self)
        self.actionOptions = action.ActionOptions(self)

        # add actions to menu
        self.addAction(self.actionSshPresets)
        #self.addAction(self.actionEnvPresets)
        self.addSeparator()
        self.addAction(self.actionOptions)
