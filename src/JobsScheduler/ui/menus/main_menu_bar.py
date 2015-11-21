# -*- coding: utf-8 -*-
"""
Main window menus
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets
import ui.actions.main_menu_actions as action
from data.states import TaskStatus


class MainMenuBar(QtWidgets.QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MainMenuBar")

        # menus
        self.app = AppMenu(self)
        self.multiJob = MultiJobMenu(self)
        self.settings = SettingsMenu(self)

        # add menus to main menu
        self.addAction(self.app.menuAction())
        self.addAction(self.multiJob.menuAction())
        self.addAction(self.settings.menuAction())


class AppMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Menu")
        self.setObjectName("appMenu")

        # app actions
        self.actionExit = action.ActionExit(self)

        # add actions to menu
        self.addAction(self.actionExit)


class MultiJobMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("MultiJob")
        self.setObjectName("multiJobMenu")

        # creating actions
        self.actionAddMultiJob = action.ActionAddMultiJob(self)
        self.actionEditMultiJob = action.ActionEditMultiJob(self)
        self.actionCopyMultiJob = action.ActionCopyMultiJob(self)
        self.actionDeleteMultiJob = action.ActionDeleteMultiJob(self)

        # control actions
        self.actionRunMultiJob = action.ActionRunMultiJob(self)
        self.actionPauseMultiJob = action.ActionPauseMultiJob(self)
        self.actionResumeMultiJob = action.ActionResumeMultiJob(self)
        self.actionStopMultiJob = action.ActionStopMultiJob(self)
        self.actionRestartMultiJob = action.ActionRestartMultiJob(self)

        # add actions to menu
        self.addAction(self.actionAddMultiJob)
        self.addAction(self.actionEditMultiJob)
        self.addAction(self.actionCopyMultiJob)
        self.addAction(self.actionDeleteMultiJob)
        self.addSeparator()
        self.addAction(self.actionRunMultiJob)
        self.addAction(self.actionPauseMultiJob)
        self.addAction(self.actionResumeMultiJob)
        self.addAction(self.actionStopMultiJob)
        self.addAction(self.actionRestartMultiJob)

    def update_locks(self, task_status=None):
        if task_status is TaskStatus.none:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(False)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(False)

            self.actionRunMultiJob.setDisabled(False)
            self.actionPauseMultiJob.setDisabled(True)
            self.actionResumeMultiJob.setDisabled(True)
            self.actionStopMultiJob.setDisabled(True)
            self.actionRestartMultiJob.setDisabled(True)

        elif task_status is TaskStatus.installation:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(True)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(True)

            self.actionRunMultiJob.setDisabled(True)
            self.actionPauseMultiJob.setDisabled(True)
            self.actionResumeMultiJob.setDisabled(True)
            self.actionStopMultiJob.setDisabled(True)
            self.actionRestartMultiJob.setDisabled(True)

        elif task_status is TaskStatus.running:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(True)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(True)

            self.actionRunMultiJob.setDisabled(True)
            self.actionPauseMultiJob.setDisabled(False)
            self.actionResumeMultiJob.setDisabled(True)
            self.actionStopMultiJob.setDisabled(False)
            self.actionRestartMultiJob.setDisabled(False)

        elif task_status is TaskStatus.pausing:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(True)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(True)

            self.actionRunMultiJob.setDisabled(True)
            self.actionPauseMultiJob.setDisabled(True)
            self.actionResumeMultiJob.setDisabled(True)
            self.actionStopMultiJob.setDisabled(True)
            self.actionRestartMultiJob.setDisabled(True)

        elif task_status is TaskStatus.pausing:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(True)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(True)

            self.actionRunMultiJob.setDisabled(True)
            self.actionPauseMultiJob.setDisabled(True)
            self.actionResumeMultiJob.setDisabled(True)
            self.actionStopMultiJob.setDisabled(True)
            self.actionRestartMultiJob.setDisabled(True)

        elif task_status is TaskStatus.paused:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(True)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(True)

            self.actionRunMultiJob.setDisabled(True)
            self.actionPauseMultiJob.setDisabled(True)
            self.actionResumeMultiJob.setDisabled(False)
            self.actionStopMultiJob.setDisabled(True)
            self.actionRestartMultiJob.setDisabled(True)

        elif task_status is TaskStatus.resuming:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(True)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(True)

            self.actionRunMultiJob.setDisabled(True)
            self.actionPauseMultiJob.setDisabled(True)
            self.actionResumeMultiJob.setDisabled(True)
            self.actionStopMultiJob.setDisabled(True)
            self.actionRestartMultiJob.setDisabled(True)

        else:
            self.actionAddMultiJob.setDisabled(False)
            self.actionEditMultiJob.setDisabled(False)
            self.actionCopyMultiJob.setDisabled(False)
            self.actionDeleteMultiJob.setDisabled(False)

            self.actionRunMultiJob.setDisabled(False)
            self.actionPauseMultiJob.setDisabled(False)
            self.actionResumeMultiJob.setDisabled(False)
            self.actionStopMultiJob.setDisabled(False)
            self.actionRestartMultiJob.setDisabled(False)


class SettingsMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Settings")
        self.setObjectName("settingsMenu")

        # preset actions
        self.actionSshPresets = action.ActionSshPresets(self)
        self.actionPbsPresets = action.ActionPbsPresets(self)
        self.actionResourcesPresets = action.ActionResourcesPresets(self)
        self.actionEnvPresets = action.ActionEnvPresets(self)

        # add actions to menu
        self.addAction(self.actionSshPresets)
        self.addAction(self.actionPbsPresets)
        self.addAction(self.actionResourcesPresets)
        self.addAction(self.actionEnvPresets)
