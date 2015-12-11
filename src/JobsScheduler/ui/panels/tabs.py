# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import datetime
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

    def reload_view(self, mj):
        self.ui.logsTab.reload_view(mj.get_logs())
        self.ui.resultsTab.reload_view(mj.get_results())
        if mj.jobs is not None:
            self.ui.jobsTab.reload_items(mj.jobs)
        else:
            self.ui.jobsTab.ui.treeWidget.clear()


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
        self.time_format = "%d. %m. %y; %H:%M:%S"
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.horizontalLayout.addWidget(self.ui.treeWidget)
        self.setLayout(self.ui.horizontalLayout)

    def resize_all_columns_to_contents(self):
        for idx, header in enumerate(self.headers):
            self.resizeColumnToContents(idx)


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
        self.ui.headers = ["Name", "Insert Time", "Queued Time", "Start Time",
                           "Run Interval", "Status"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)

    @staticmethod
    def _update_item(item, job, time_format):
        item.setText(0, job.name)
        item.setText(1, datetime.datetime.fromtimestamp(
                job.insert_time).strftime(time_format))
        if job.queued_time:
            item.setText(2, datetime.datetime.fromtimestamp(
                job.queued_time).strftime(time_format))
        else:
            item.setText(2, "Not Queued Yet")
        if job.start_time:
            item.setText(3, datetime.datetime.fromtimestamp(
                job.start_time).strftime(time_format))
        else:
            item.setText(3, "Not Started Yet")
        item.setText(4, str(datetime.timedelta(seconds=job.run_interval)))
        item.setText(5, TaskStatus(job.status).name)
        return item

    def reload_items(self, jobs):
        self.ui.treeWidget.clear()
        for job in jobs:
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            self._update_item(row, job, self.time_format)
        self.ui.treeWidget.resizeColumnToContents(0)


class FilesTab(AbstractTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FilesTab")
        self.ui.headers = ["Name", "Size", "Modification", "Path"]
        self.ui.treeWidget.setHeaderLabels(self.ui.headers)
        self.ui.treeWidget.itemDoubleClicked.connect(
            lambda clicked_item, clicked_col: QDesktopServices.openUrl(
                QUrl.fromLocalFile(clicked_item.text(3))))

    @staticmethod
    def _update_item(item, f, time_format):
        item.setText(0, f.file_name)
        item.setText(1, f.file_size)
        item.setText(2, datetime.datetime.fromtimestamp(
                f.modification_time).strftime(time_format))
        item.setText(3, f.file_path)

        return item

    def reload_view(self, file_objects):
        self.ui.treeWidget.clear()
        for f in file_objects:
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            self._update_item(row, f, self.time_format)
        self.ui.treeWidget.resizeColumnToContents(0)
        self.ui.treeWidget.resizeColumnToContents(1)
        self.ui.treeWidget.resizeColumnToContents(2)


class LogsTab(FilesTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logsTab")


class ResultsTab(FilesTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultsTab")
