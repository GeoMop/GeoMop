# -*- coding: utf-8 -*-
"""
Main window menus
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets
import ui.actions.main_menu_actions as action
from data.states import TaskStatus
from geomop_widgets import ProjectMenu
from ui.data.data_structures import DataContainer


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
        self.analysis = AnalysisMenu(self)
        self.project = ProjectMenu(self, {})

        # add menus to main menu
        self.addAction(self.app.menuAction())
        self.addAction(self.multiJob.menuAction())
        self.addAction(self.analysis.menuAction())
        self.addAction(self.project.menuAction())
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

        if DataContainer.DEBUG_MODE:
            self.addAction(self.actionPauseMultiJob)
            self.addAction(self.actionResumeMultiJob)

        self.addAction(self.actionStopMultiJob)
        self.addAction(self.actionRestartMultiJob)

        self.lock_as_empty()

    def lock_as_none(self):
        """
        Locks to state None
        :return:
        """
        my_locks = dict(add=False, edit=False, copy=False, delete=False,
                        run=False, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_installation(self):
        """
        Locks to state Installation
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=True,
                        run=True, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_queued(self):
        """
        Locks to state queued
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=True,
                        run=True, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_running(self):
        """
        Locks to state Running
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=True,
                        run=True, pause=False, resume=True, stop=False,
                        restart=False)
        self.lock_as(**my_locks)

    def lock_as_pausing(self):
        """
        Locks to state Pausing
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=True,
                        run=True, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_paused(self):
        """
        Locks to state Paused
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=True,
                        run=True, pause=True, resume=False, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_resuming(self):
        """
        Locks to state Resuming
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=True,
                        run=True, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_finished(self):
        """
        Locks to state finished
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=False, delete=False,
                        run=False, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as_empty(self):
        """
        Locks as if no MultiJob is selected
        :return:
        """
        my_locks = dict(add=False, edit=True, copy=True, delete=True,
                        run=True, pause=True, resume=True, stop=True,
                        restart=True)
        self.lock_as(**my_locks)

    def lock_as(self, add, edit, copy, delete, run, pause, resume, stop,
                restart):
        """
        Locks UI by parameters
        :param add: Boolean to lock given property
        :param edit: Boolean to lock given property
        :param copy: Boolean to lock given property
        :param delete: Boolean to lock given property
        :param run: Boolean to lock given property
        :param pause: Boolean to lock given property
        :param resume: Boolean to lock given property
        :param stop: Boolean to lock given property
        :param restart: Boolean to lock given property
        :return:
        """
        self.actionAddMultiJob.setDisabled(add)
        self.actionEditMultiJob.setDisabled(edit)
        self.actionCopyMultiJob.setDisabled(copy)
        self.actionDeleteMultiJob.setDisabled(delete)

        self.actionRunMultiJob.setDisabled(run)
        self.actionPauseMultiJob.setDisabled(pause)
        self.actionResumeMultiJob.setDisabled(resume)
        self.actionStopMultiJob.setDisabled(stop)
        self.actionRestartMultiJob.setDisabled(restart)

    def lock_all(self, lock=True):
        """
        Locks all by lock
        :param lock: Boolean that applies to all locks
        :return:
        """
        my_locks = dict(add=lock, edit=lock, copy=lock, delete=lock,
                        run=lock, pause=lock, resume=lock, stop=lock,
                        restart=lock)
        self.lock_as(**my_locks)

    def lock(self):
        """
        Locks all
        :return:
        """
        self.lock_all(True)

    def unlock(self):
        """
        Unlocks all
        :return:
        """
        self.lock_all(False)

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
        elif task_status is TaskStatus.queued:
            self.lock_as_queued()
        elif task_status is TaskStatus.running:
            self.lock_as_running()
        elif task_status is TaskStatus.pausing:
            self.lock_as_pausing()
        elif task_status is TaskStatus.paused:
            self.lock_as_paused()
        elif task_status is TaskStatus.resuming:
            self.lock_as_resuming()
        elif task_status is TaskStatus.finished:
            self.lock_as_finished()
        else:
            self.lock_as_empty()


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


class AnalysisMenu(QtWidgets.QMenu):
    """
    Analysis menu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Analysis")
        self.setObjectName("analysisMenu")

        # creating actions
        self.actionCreateAnalysis = action.ActionCreateAnalysis(self)

        # add actions to menu
        self.addAction(self.actionCreateAnalysis)
