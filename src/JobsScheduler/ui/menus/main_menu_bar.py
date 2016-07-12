# -*- coding: utf-8 -*-
"""
Main window menus
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets
import ui.actions.main_menu_actions as action
from data.states import TaskStatus, MultijobActions, TASK_STATUS_PERMITTED_ACTIONS
from ui.menus import AnalysisMenu


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

        # add actions to menu
        self.addAction(self.actionExit)
        self.addAction(self.actionLog)


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
        self.actionRunMultiJob = action.ActionRunMultiJob(self)
        self.actionStopMultiJob = action.ActionStopMultiJob(self)

        # add actions to menu
        self.addAction(self.actionAddMultiJob)
        self.addAction(self.actionReuseMultiJob)
        self.addAction(self.actionDeleteRemote)
        self.addAction(self.actionDeleteMultiJob)
        self.addSeparator()
        self.addAction(self.actionRunMultiJob)
        self.addAction(self.actionStopMultiJob)

        self.lockable_actions = {
            MultijobActions.delete: self.actionDeleteMultiJob,
            MultijobActions.run: self.actionRunMultiJob,
            MultijobActions.stop: self.actionStopMultiJob
        }

        self.lock_by_status()

    def lock_by_status(self, task_status=None):
        """
        Locks UI actions based on selected MultiJob. If status is None then
        it works like unlock.
        :param task_status: Status that controls the locks.
        :return:
        """
        if task_status is None:
            task_status = TaskStatus.none
        for mj_action, menu_action in self.lockable_actions.items():
            if (task_status, mj_action) in TASK_STATUS_PERMITTED_ACTIONS:
                menu_action.setDisabled(False)
            else:
                menu_action.setDisabled(True)


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
        self.actionOptions = action.ActionOptions(self)

        # add actions to menu
        self.addAction(self.actionSshPresets)
        self.addAction(self.actionPbsPresets)
        self.addAction(self.actionResourcesPresets)
        self.addAction(self.actionEnvPresets)
        self.addSeparator()
        self.addAction(self.actionOptions)
