# -*- coding: utf-8 -*-
"""
Actions used by main menu.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class ActionExit(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Exit")
        self.setShortcut("Ctrl+Q")
        self.setObjectName("actionExit")


class ActionLog(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Log")
        self.setShortcut("Ctrl+L")
        self.setObjectName("actionLog")


class ActionAddMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Add")
        self.setShortcut("Alt+A")
        self.setObjectName("actionAddMultiJob")


class ActionEditMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Edit")
        self.setShortcut("Alt+E")
        self.setObjectName("actionEditMultiJob")


class ActionCopyMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Copy")
        self.setShortcut("Alt+C")
        self.setObjectName("actionCopyMultiJob")


class ActionDeleteMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Delete")
        self.setShortcut("Alt+D")
        self.setObjectName("actionDeleteMultiJob")


class ActionRunMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Run")
        self.setShortcut("Ctrl+R")
        self.setObjectName("actionRunMultiJob")


class ActionPauseMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Pause")
        self.setShortcut("Ctrl+P")
        self.setObjectName("actionPauseMultiJob")


class ActionResumeMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Resume")
        self.setShortcut("Ctrl+U")
        self.setObjectName("actionResumeMultiJob")


class ActionStopMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Stop")
        self.setShortcut("Ctrl+S")
        self.setObjectName("actionStopMultiJob")


class ActionRestartMultiJob(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Restart")
        self.setShortcut("Ctrl+E")
        self.setObjectName("actionRestartMultiJob")


class ActionSshPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("SSH Connections")
        self.setShortcut("Shift+S")
        self.setObjectName("actionSshPresets")


class ActionPbsPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("PBS Presets")
        self.setShortcut("Shift+P")
        self.setObjectName("actionPbsPresets")


class ActionResourcesPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Resources")
        self.setShortcut("Shift+R")
        self.setObjectName("actionResourcesPresets")


class ActionEnvPresets(QtWidgets.QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("Environments")
        self.setShortcut("Shift+E")
        self.setObjectName("actionEnvPresets")
