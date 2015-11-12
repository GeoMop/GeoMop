# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(Tabs, self).__init__(parent)
        self.ui = UiTabs()
        self.ui.setup_ui(self)
        self.show()

    def reload_view(self, results):
        self.ui.logsTab.reload_view(results["logs"])
        self.ui.confTab.reload_view(results["conf"])
        self.ui.messagesTab.reload_view(results["messages"])


class UiTabs(object):

    def setup_ui(self, tab_widget):
        tab_widget.setObjectName("MultiJobInfoTab")
        self.logsTab = FilesTab(tab_widget)
        self.confTab = FilesTab(tab_widget)
        self.messagesTab = MessagesTab(tab_widget)
        tab_widget.addTab(self.messagesTab, "Messages")
        tab_widget.addTab(self.logsTab, "Logs")
        tab_widget.addTab(self.confTab, "Config")


class FilesTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("filesTab")
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.headers = ["Filename", "Path"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.treeWidget.itemDoubleClicked.connect(
            lambda clicked_item, clicked_col: QDesktopServices.openUrl(
                QUrl.fromLocalFile(clicked_item.text(1))))
        self.ui.treeWidget.resizeColumnToContents(0)

        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def reload_view(self, path):
        file_names = [f for f in os.listdir(path) if os.path.isfile(
            os.path.join(path, f))]
        self.ui.treeWidget.clear()
        for idx, file_name in enumerate(file_names):
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            row.setText(0, file_name)
            row.setText(1, os.path.join(path, file_name))
        self.ui.treeWidget.resizeColumnToContents(0)


class MessagesTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("messagesTab")
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.headers = ["Message"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def reload_view(self, messages):
        self.ui.treeWidget.clear()
        for idx, mess in enumerate(messages):
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            row.setText(0, mess.__str__())
        self.ui.treeWidget.resizeColumnToContents(0)
