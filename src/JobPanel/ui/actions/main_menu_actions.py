# -*- coding: utf-8 -*-
"""
Actions used by main menu.
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets

def ActionExit(parent=None):
    action = QtWidgets.QAction(parent)
    action.setText("Exit")
    action.setShortcut("Ctrl+Q")
    action.setObjectName("actionExit")
    return action

def ActionLog(parent=None):
    action = QtWidgets.QAction(parent)
    action.setText("Log")
    action.setShortcut("Ctrl+L")
    action.setObjectName("actionLog")
    return action
        
def ActionRemLog(parent=None):
    action = QtWidgets.QAction(parent)
    action.setText("Remove Log")
    action.setShortcut("Ctrl+R")
    action.setObjectName("actionRemLog")
    return action

def ActionAddMultiJob(parent=None):
    action = QtWidgets.QAction(parent)
    action.setText("Add")
    action.setShortcut("Alt+A")
    action.setObjectName("actionAddMultiJob")
    return action

def ActionEditMultiJob(parent=None):
    action = QtWidgets.QAction(parent)   
    action.setText("Edit")
    action.setShortcut("Alt+E")
    action.setObjectName("actionEditMultiJob")
    return action

def ActionReuseMultiJob(parent=None):
    action = QtWidgets.QAction(parent) 
    action.setText("Reuse")
    action.setShortcut("Alt+C")
    action.setObjectName("actionReuseMultiJob")
    return action

def ActionDeleteMultiJob(parent=None):
    action = QtWidgets.QAction(parent)    
    action.setText("Delete MultiJob")
    action.setObjectName("actionDeleteMultiJob")
    return action        
        
def ActionSendReport(parent=None):
    action = QtWidgets.QAction(parent)   
    action.setText("Create Report")
    action.setObjectName("actionSendReport")    
    return action

def ActionDeleteRemote(parent=None):
    action = QtWidgets.QAction(parent)    
    action.setText("Delete Remote")
    action.setObjectName("actionDeleteRemote")
    return action

def ActionDownloadWholeMultiJob(parent=None):
    action = QtWidgets.QAction(parent) 
    action.setText("Download Whole MultiJob")
    action.setObjectName("actionDownloadWholeMultiJob")
    return action

def ActionResumeMultiJob(parent=None):
    action = QtWidgets.QAction(parent)    
    action.setText("Resume")
    action.setShortcut("Ctrl+U")
    action.setObjectName("actionResumeMultiJob")
    return action

def ActionStopMultiJob(parent=None):
    action = QtWidgets.QAction(parent)  
    action.setText("Stop")
    action.setShortcut("Ctrl+S")
    action.setObjectName("actionStopMultiJob")
    return action

def ActionSshPresets(parent=None):
    action = QtWidgets.QAction(parent)    
    action.setText("SSH hosts")
    action.setShortcut("Shift+S")
    action.setObjectName("actionSshPresets")
    return action

def ActionEnvPresets(parent=None):
    action = QtWidgets.QAction(parent)     
    action.setText("Environments")
    action.setShortcut("Shift+E")
    action.setObjectName("actionEnvPresets")
    return action

def ActionOptions(parent=None):
    action = QtWidgets.QAction(parent)    
    action.setText("Set workspace")
    action.setShortcut("Shift+O")
    action.setObjectName("actionOptions")
    return action