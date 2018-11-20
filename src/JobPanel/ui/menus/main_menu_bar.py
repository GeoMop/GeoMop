# -*- coding: utf-8 -*-
"""
Main window menus
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets
from JobPanel.data.states import TaskStatus, MultijobActions, TASK_STATUS_PERMITTED_ACTIONS
from JobPanel.ui.menus import AnalysisMenu


def create_action(parent, text, shortcut="", object_name=""):
    action = QtWidgets.QAction(parent)
    action.setText(text)
    action.setShortcut(shortcut)
    action.setObjectName(object_name)
    return action


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
        self.actionExit = create_action(self, "Exit", "Ctrl+Q", "actionExit")
        self.actionLog = create_action(self, "Log", "Ctrl+L", "actionLog")
        self.actionRemLog = create_action(self, "Remove Log", "Ctrl+R", "actionRemLog")

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
        self.actionAddMultiJob = create_action(self, "Add", "Alt+A", "actionAddMultiJob")
        self.actionReuseMultiJob = create_action(self, "Reuse", "Alt+C", "actionReuseMultiJob")
        self.actionDeleteRemote = create_action(self, "Delete Remote", "actionDeleteRemote")
        self.actionDeleteMultiJob = create_action(self, "Delete MultiJob", "actionDeleteMultiJob")

        # control actions
        self.actionStopMultiJob = create_action(self, "Stop", "Ctrl+S", "actionStopMultiJob")
        self.actionSendReport = create_action(self, "Create Report", "actionSendReport")

        self.actionDownloadWholeMultiJob = create_action(self, "Download Whole MultiJob", "actionDownloadWholeMultiJob")

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

        self.lock_by_mj()

    def lock_by_mj(self, mj=None):
        """
        Locks UI actions based on selected MultiJob.
        :param mj: MultiJob that controls the locks.
        :return:
        """
        if mj is not None:
            for mj_action, menu_action in self.lockable_actions.items():
                menu_action.setDisabled(mj.is_action_forbidden(mj_action))
        else:
            for mj_action, menu_action in self.lockable_actions.items():
                menu_action.setDisabled(True)

    def lock_by_selection(self, multijobs, mj_ids):
        """
        Locks UI actions based on selected MultiJobs.
        Disables those actions in UI, which don't make sense.
        :param multijobs: list of all MultiJobs
        :param mj_ids: ids of selected MultiJobs
        """

        self.actionDownloadWholeMultiJob.setDisabled(True)
        self.actionReuseMultiJob.setDisabled(True)
        self.actionSendReport.setDisabled(True)

        remote_delete = all([multijobs[mj_id].is_action_forbidden(MultijobActions.delete_remote) for mj_id in mj_ids])
        self.actionDeleteRemote.setDisabled(remote_delete)

        delete = all([multijobs[mj_id].is_action_forbidden(MultijobActions.delete) for mj_id in mj_ids])
        self.actionDeleteMultiJob.setDisabled(delete)

        stop = all([multijobs[mj_id].is_action_forbidden(MultijobActions.stop) for mj_id in mj_ids])
        self.actionStopMultiJob.setDisabled(stop)


class SettingsMenu(QtWidgets.QMenu):
    """
    Settings sub menu.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Settings")
        self.setObjectName("settingsMenu")

        # preset actions
        self.actionSshPresets = create_action(self, "SSH hosts", "Shift+S", "actionSshPresets")
        self.actionEnvPresets = create_action(self, "Environments", "Shift+E", "actionEnvPresets")
        self.actionOptions = create_action(self, "Set workspace", "Shift+O", "actionOptions")

        # add actions to menu
        self.addAction(self.actionSshPresets)
        #self.addAction(self.actionEnvPresets)
        self.addSeparator()
        self.addAction(self.actionOptions)
