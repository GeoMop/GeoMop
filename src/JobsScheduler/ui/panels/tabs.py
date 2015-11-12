# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import copy
import datetime
import os

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from data.states import JobState, TaskStatus


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

        job1 = JobState("job1")
        job1.insert_time = datetime.datetime.now()
        job1.qued_time = datetime.datetime.now()
        job1.start_time = datetime.datetime.now()
        job1.run_interval = 10
        job1.status = TaskStatus.running
        job2 = copy.deepcopy(job1)
        job2.name = "job2"
        jobs = list()
        jobs.append(job1)
        jobs.append(job2)
        self.ui.jobsTab.reload_view(jobs)


class UiTabs(object):

    def setup_ui(self, tab_widget):
        tab_widget.setObjectName("MultiJobInfoTab")
        self.overviewTab = OverviewTab(tab_widget)
        self.jobsTab = JobsTab(tab_widget)
        self.resultsTab = ResultsTab(tab_widget)
        self.messagesTab = MessagesTab(tab_widget)
        self.logsTab = FilesTab(tab_widget)
        self.confTab = FilesTab(tab_widget)
        tab_widget.addTab(self.overviewTab, "Overview")
        tab_widget.addTab(self.jobsTab, "Jobs")
        tab_widget.addTab(self.resultsTab, "Results")
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


class OverviewTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overviewTab")
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.headers = ["Overview"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def reload_view(self, messages):
        pass


class JobsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("jobsTab")
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.headers = ["Name", "Insert Time", "Qued Time", "Start Time",
                           "Run Interval", "Status"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def reload_view(self, jobs):
        self.ui.treeWidget.clear()
        for idx, job in enumerate(jobs):
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            row.setText(0, job.name)
            row.setText(1, str(job.insert_time))
            row.setText(2, str(job.qued_time))
            row.setText(3, str(job.start_time))
            row.setText(4, str(job.run_interval))
            row.setText(5, job.status.name)
        self.ui.treeWidget.resizeColumnToContents(0)


class ResultsTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultsTab")
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.headers = ["Results"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def reload_view(self, messages):
        pass
