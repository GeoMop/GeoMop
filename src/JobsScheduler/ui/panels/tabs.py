# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import time
import os

import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from data.states import TaskStatus


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(Tabs, self).__init__(parent)
        self.ui = UiTabs()
        self.ui.setup_ui(self)
        self.show()

    def reload_view(self, results):
        self.ui.logsTab.reload_view(results["logs"])
        self.ui.jobsTab.reload_items(results["jobs"])


class UiTabs(object):

    def setup_ui(self, tab_widget):
        tab_widget.setObjectName("MultiJobInfoTab")
        self.overviewTab = OverviewTab(tab_widget)
        self.jobsTab = JobsTab(tab_widget)
        self.resultsTab = ResultsTab(tab_widget)
        self.logsTab = LogsTab(tab_widget)
        tab_widget.addTab(self.overviewTab, "Overview")
        tab_widget.addTab(self.jobsTab, "Jobs")
        tab_widget.addTab(self.resultsTab, "Results")
        tab_widget.addTab(self.logsTab, "Logs")


class AbstractTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("abstractTab")
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.headers = ["Header"]
        self.time_format = "%H:%M:%S %d/%m/%y"
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def resize_all_columns_to_contents(self):
        for idx, header in enumerate(self.headers):
            self.resizeColumnToContents(idx)


class FilesTab(AbstractTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("filesTab")
        self.ui.headers = ["Filename", "Path"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.itemDoubleClicked.connect(
            lambda clicked_item, clicked_col: QDesktopServices.openUrl(
                QUrl.fromLocalFile(clicked_item.text(1))))

    def reload_view(self, path):
        if not os.path.exists(path):
            return
        file_names = [f for f in os.listdir(path) if os.path.isfile(
            os.path.join(path, f))]
        self.ui.treeWidget.clear()
        for idx, file_name in enumerate(file_names):
            if len(file_name)<5 or file_name[-4:] != ".log":
                continue
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            row.setText(0, file_name)
            row.setText(1, os.path.join(path, file_name))


class OverviewTab(AbstractTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("overviewTab")
        self.ui.headers = ["Overview"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)

    def reload_view(self, messages):
        pass


class JobsTab(AbstractTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("jobsTab")
        self.ui.headers = ["Name", "Insert Time", "Qued Time", "Start Time",
                           "Run Interval", "Status"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)

    @staticmethod
    def _update_item(item, job, time_format):
        item.setText(0, job.name)
        item.setText(1, time.strftime(
            time_format, time.gmtime(job.insert_time)))
        item.setText(2, time.strftime(
            time_format, time.gmtime(job.qued_time)))
        item.setText(3, time.strftime(
            time_format, time.gmtime(job.start_time)))
        item.setText(4, str(job.run_interval))
        item.setText(5, TaskStatus(job.status).name)
        return item

    def reload_items(self, jobs):
        self.ui.treeWidget.clear()
        for job in jobs:
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            self._update_item(row, job, self.time_format)
        self.ui.treeWidget.resizeColumnToContents(0)


class ResultsTab(AbstractTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultsTab")
        self.ui.headers = ["Results"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)

    def reload_view(self, messages):
        pass


class LogsTab(FilesTab):
    def __init__(self, parent=None):
        super().__init__(parent)
