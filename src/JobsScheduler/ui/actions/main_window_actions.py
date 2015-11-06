# -*- coding: utf-8 -*-
"""
Main window actions
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class ActionExit(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionExit, self).__init__(parent)
        self.setText("Exit")
        self.setShortcut("Ctrl+Q")
        self.setObjectName("actionExit")


class ActionAddMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionAddMultiJob, self).__init__(parent)
        self.setText("Add")
        self.setShortcut("Alt+A")
        self.setObjectName("actionAddMultiJob")


class ActionEditMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionEditMultiJob, self).__init__(parent)
        self.setText("Edit")
        self.setShortcut("Alt+E")
        self.setObjectName("actionEditMultiJob")


class ActionCopyMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionCopyMultiJob, self).__init__(parent)
        self.setText("Copy")
        self.setShortcut("Alt+C")
        self.setObjectName("actionCopyMultiJob")


class ActionDeleteMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionDeleteMultiJob, self).__init__(parent)
        self.setText("Delete")
        self.setShortcut("Alt+D")
        self.setObjectName("actionDeleteMultiJob")


class ActionRunMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionRunMultiJob, self).__init__(parent)
        self.setText("Run")
        self.setShortcut("Ctrl+R")
        self.setObjectName("actionRunMultiJob")


class ActionPauseMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionPauseMultiJob, self).__init__(parent)
        self.setText("Pause")
        self.setShortcut("Ctrl+P")
        self.setObjectName("actionPauseMultiJob")


class ActionStopMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionStopMultiJob, self).__init__(parent)
        self.setText("Stop")
        self.setShortcut("Ctrl+S")
        self.setObjectName("actionStopMultiJob")


class ActionRestartMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionRestartMultiJob, self).__init__(parent)
        self.setText("Restart")
        self.setShortcut("Ctrl+E")
        self.setObjectName("actionRestartMultiJob")


class ActionSshPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionSshPresets, self).__init__(parent)
        self.setText("SSH Connections")
        self.setShortcut("Shift+S")
        self.setObjectName("actionSshPresets")


class ActionPbsPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionPbsPresets, self).__init__(parent)
        self.setText("PBS Presets")
        self.setShortcut("Shift+P")
        self.setObjectName("actionPbsPresets")


class ActionResourcesPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionResourcesPresets, self).__init__(parent)
        self.setText("Resources")
        self.setShortcut("Shift+R")
        self.setObjectName("actionResourcesPresets")


class ActionEnvPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super(ActionEnvPresets, self).__init__(parent)
        self.setText("Environments")
        self.setShortcut("Shift+E")
        self.setObjectName("actionEnvPresets")
