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

        # add menus to main menu
        self.addAction(self.app.menuAction())
        self.addAction(self.multiJob.menuAction())
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

        # add actions to menu
        self.addAction(self.actionExit)


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

    def lock_as_none(self):
        """
        Locks to state None
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(False)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(False)

        self.actionRunMultiJob.setDisabled(False)
        self.actionPauseMultiJob.setDisabled(True)
        self.actionResumeMultiJob.setDisabled(True)
        self.actionStopMultiJob.setDisabled(True)
        self.actionRestartMultiJob.setDisabled(True)

    def lock_as_installation(self):
        """
        Locks to state Installation
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(True)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(True)

        self.actionRunMultiJob.setDisabled(True)
        self.actionPauseMultiJob.setDisabled(True)
        self.actionResumeMultiJob.setDisabled(True)
        self.actionStopMultiJob.setDisabled(True)
        self.actionRestartMultiJob.setDisabled(True)

    def lock_as_running(self):
        """
        Locks to state Running
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(True)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(True)

        self.actionRunMultiJob.setDisabled(True)
        self.actionPauseMultiJob.setDisabled(False)
        self.actionResumeMultiJob.setDisabled(True)
        self.actionStopMultiJob.setDisabled(False)
        self.actionRestartMultiJob.setDisabled(False)

    def lock_as_pausing(self):
        """
        Locks to state Pausing
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(True)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(True)

        self.actionRunMultiJob.setDisabled(True)
        self.actionPauseMultiJob.setDisabled(True)
        self.actionResumeMultiJob.setDisabled(True)
        self.actionStopMultiJob.setDisabled(True)
        self.actionRestartMultiJob.setDisabled(True)

    def lock_as_paused(self):
        """
        Locks to state Paused
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(True)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(True)

        self.actionRunMultiJob.setDisabled(True)
        self.actionPauseMultiJob.setDisabled(True)
        self.actionResumeMultiJob.setDisabled(False)
        self.actionStopMultiJob.setDisabled(True)
        self.actionRestartMultiJob.setDisabled(True)

    def lock_as_resuming(self):
        """
        Locks to state Resuming
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(True)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(True)

        self.actionRunMultiJob.setDisabled(True)
        self.actionPauseMultiJob.setDisabled(True)
        self.actionResumeMultiJob.setDisabled(True)
        self.actionStopMultiJob.setDisabled(True)
        self.actionRestartMultiJob.setDisabled(True)

    def unlock(self):
        """
        Unlocks all actions
        :return:
        """
        self.actionAddMultiJob.setDisabled(False)
        self.actionEditMultiJob.setDisabled(False)
        self.actionCopyMultiJob.setDisabled(False)
        self.actionDeleteMultiJob.setDisabled(False)

        self.actionRunMultiJob.setDisabled(False)
        self.actionPauseMultiJob.setDisabled(False)
        self.actionResumeMultiJob.setDisabled(False)
        self.actionStopMultiJob.setDisabled(False)
        self.actionRestartMultiJob.setDisabled(False)

    def lock_by_status(self, task_status=None):
        """
        Locks UI actions based on selected MultiJob. If status is None then
        it works like unlock.
        :param task_status: Status that controls the locks.
        :return:
        """
        if task_status is TaskStatus.none:
            self.lock_as_none()
        elif task_status is TaskStatus.installation:
            self.lock_as_installation()
        elif task_status is TaskStatus.running:
            self.lock_as_running()
        elif task_status is TaskStatus.pausing:
            self.lock_as_pausing()
        elif task_status is TaskStatus.paused:
            self.lock_as_paused()
        elif task_status is TaskStatus.resuming:
            self.lock_as_resuming()
        else:
            self.unlock()


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
        self.actionPbsPresets = action.ActionPbsPresets(self)
        self.actionResourcesPresets = action.ActionResourcesPresets(self)
        self.actionEnvPresets = action.ActionEnvPresets(self)

        # add actions to menu
        self.addAction(self.actionSshPresets)
        self.addAction(self.actionPbsPresets)
        self.addAction(self.actionResourcesPresets)
        self.addAction(self.actionEnvPresets)
