#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main window module
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets
from panels.multijob_table import UiMultijobTable
from panels.multijob_infotab import UiMultijobInfotab


class UiMainWindow(QtWidgets.QMainWindow):
    """
    Main window class
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.show()

    def setup_ui(self):
        """
        Setup basic UI
        """
        # main window
        self.resize(600, 400)
        self.setObjectName("MainWindow")
        self.setWindowTitle('Jobs Scheduler')

        # layout
        self.verticalLayoutWidget = QtWidgets.QWidget(self)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.setCentralWidget(self.verticalLayoutWidget)

        # menubar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

        # menubarMenu
        self.menubarMenu = self.menubar.addMenu('&Menu')
        # menubarMenu_exit_action
        self.menu_exit_action = QtWidgets.QAction('&Exit', self)
        self.menu_exit_action.setShortcut('Ctrl+Q')
        self.menu_exit_action.setStatusTip('Exit application')
        self.menubarMenu.addAction(self.menu_exit_action)

        # menubarMultijob
        self.menubarMultijob = self.menubar.addMenu('&MultiJob')
        # menubarMultijob_add_action
        self.multijob_add_action = QtWidgets.QAction('&Add', self)
        self.multijob_add_action.setShortcut('Alt+A')
        self.multijob_add_action.setStatusTip('Add new MultiJob')
        self.menubarMultijob.addAction(self.multijob_add_action)
        # menubarMultijob_copy_or_edit_action
        self.multijob_copy_edit_action = QtWidgets.QAction('&Copy | Edit',
                                                           self)
        self.multijob_copy_edit_action.setShortcut('Alt+C')
        self.multijob_copy_edit_action.setStatusTip('Copy or Edit MultiJob')
        self.menubarMultijob.addAction(self.multijob_copy_edit_action)
        # menubarMultijob_run_or_stop_action
        self.multijob_run_stop_action = QtWidgets.QAction('&Run | Stop', self)
        self.multijob_run_stop_action.setShortcut('Alt+R')
        self.multijob_run_stop_action.setStatusTip('Run or Stop selected '
                                                   'MultiJob')
        self.menubarMultijob.addAction(self.multijob_run_stop_action)
        # menubarMultijob_delete_action
        self.multijob_delete_action = QtWidgets.QAction('&Delete', self)
        self.multijob_delete_action.setShortcut('Alt+D')
        self.multijob_delete_action.setStatusTip('Delete selected MultiJob')
        self.menubarMultijob.addAction(self.multijob_delete_action)

        # settings
        self.menubarSettings = self.menubar.addMenu('&Settings')
        # menubarSettings_resource_action
        self.settings_resource_action = QtWidgets.QAction('&Resource', self)
        self.settings_resource_action.setShortcut('Shift+R')
        self.settings_resource_action.setStatusTip('Show resources')
        self.menubarSettings.addAction(self.settings_resource_action)
        # menubarSettings_ssh_action
        self.settings_ssh_action = QtWidgets.QAction('&SSH Connections', self)
        self.settings_ssh_action.setShortcut('Shift+S')
        self.settings_ssh_action.setStatusTip('Show ssh connections')
        self.menubarSettings.addAction(self.settings_ssh_action)
        # menubarSettings_pbss_action
        self.settings_pbss_action = QtWidgets.QAction('&PBSs', self)
        self.settings_pbss_action.setShortcut('Shift+P')
        self.settings_pbss_action.setStatusTip('Show available PBSs')
        self.menubarSettings.addAction(self.settings_pbss_action)

        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.showMessage("Ready", 2000)
        self.setStatusBar(self.statusbar)

        # MultijobTable
        self.tableView = UiMultijobTable(self.verticalLayoutWidget)
        self.tableView.setObjectName("tableView")
        self.verticalLayout.addWidget(self.tableView)

        # MultijobInfotab
        self.tabWidget = UiMultijobInfotab(self.verticalLayoutWidget)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)
