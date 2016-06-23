# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import datetime
from PyQt5 import QtCore
import PyQt5.QtWidgets as QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from data.states import TaskStatus
from .overview import ERROR_BRUSH


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(Tabs, self).__init__(parent)
        self.ui = UiTabs()
        self.ui.setup_ui(self)
        self.show()

    def reload_view(self, mj):
        self.ui.jobsTab.reload_view(mj.get_jobs())
        self.ui.resultsTab.reload_view(mj.get_results())
        self.ui.logsTab.reload_view(mj.get_logs())
        self.ui.confTab.reload_view(mj.get_configs())


class UiTabs(object):

    def setup_ui(self, tab_widget):
        tab_widget.setObjectName("tabs")
        # self.overviewTab = OverviewTab(tab_widget)
        self.jobsTab = JobsTab(tab_widget)
        self.resultsTab = ResultsTab(tab_widget)
        self.logsTab = LogsTab(tab_widget)
        self.confTab = ConfigTab(tab_widget)

        # tab_widget.addTab(self.overviewTab, "Overview")
        tab_widget.addTab(self.jobsTab, "Jobs")
        tab_widget.addTab(self.resultsTab, "Results")
        tab_widget.addTab(self.logsTab, "Logs")
        tab_widget.addTab(self.confTab, "Config")

        # config tab hidden if not in --debug mode
        if True:  # cfg.config.DEBUG_MODE:
            # ToDo Implement as config
            tab_widget.removeTab(3)


class AbstractTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("abstractTab")
        self.time_format = "%X %x"
        self.ui = QtWidgets.QWidget(self)
        self.ui.horizontalLayout = QtWidgets.QHBoxLayout(self.ui)
        self.ui.horizontalLayout.setObjectName("horizontalLayout")
        self.ui.treeWidget = QtWidgets.QTreeWidget(self.ui)
        self.ui.treeWidget.setAlternatingRowColors(True)
        self.ui.treeWidget.setSortingEnabled(True)
        self.ui.treeWidget.setRootIsDecorated(False)
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
        self.ui.treeWidget.header().resizeSection(1, 120)
        self.ui.treeWidget.header().resizeSection(2, 120)
        self.ui.treeWidget.header().resizeSection(3, 120)

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
        item.setText(5, str(TaskStatus(job.status)))

        item.setTextAlignment(1, QtCore.Qt.AlignRight)
        item.setTextAlignment(2, QtCore.Qt.AlignRight)
        item.setTextAlignment(3, QtCore.Qt.AlignRight)
        item.setTextAlignment(4, QtCore.Qt.AlignRight)

        # background color
        if job.status == TaskStatus.error:
            for i in range(item.columnCount()):
                item.setBackground(i, ERROR_BRUSH)

        return item

    def reload_view(self, jobs):
        self.ui.treeWidget.clear()
        for job in jobs:
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            self._update_item(row, job, self.time_format)
        self.ui.treeWidget.resizeColumnToContents(0)
        self.ui.treeWidget.resizeColumnToContents(4)


class FilesTab(AbstractTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FilesTab")
        self.headers = ["Name", "Size", "Last Modification", "Path"]
        self.files = []
        self.ui.treeWidget.setHeaderLabels(self.headers)
        self.ui.treeWidget.header().resizeSection(2, 150)
        self.ui.treeWidget.itemDoubleClicked.connect(
            lambda clicked_item, clicked_col: QDesktopServices.openUrl(
                QUrl.fromLocalFile(clicked_item.text(3))))
        QtCore.QObjectCleanupHandler().add(self.layout())
        self.ui.saveButton = QtWidgets.QPushButton('Save')
        self.ui.saveButton.setMinimumWidth(120)
        self.ui.buttonLayout = QtWidgets.QHBoxLayout()
        self.ui.buttonLayout.addWidget(self.ui.saveButton)
        self.ui.buttonLayout.addStretch(1)
        self.ui.mainLayout = QtWidgets.QVBoxLayout()
        self.ui.mainLayout.addWidget(self.ui.treeWidget)
        self.ui.mainLayout.addLayout(self.ui.buttonLayout)
        self.setLayout(self.ui.mainLayout)

    @staticmethod
    def _update_item(item, f, time_format):
        item.setText(0, f.file_name)
        item.setText(1, f.file_size)
        item.setText(2, datetime.datetime.fromtimestamp(
                f.modification_time).strftime(time_format))
        item.setText(3, f.file_path)
        item.setTextAlignment(1, QtCore.Qt.AlignRight)
        item.setTextAlignment(2, QtCore.Qt.AlignRight)
        return item

    def reload_view(self, file_objects):
        self.files = file_objects
        self.ui.treeWidget.clear()
        for f in file_objects:
            row = QtWidgets.QTreeWidgetItem(self.ui.treeWidget)
            self._update_item(row, f, self.time_format)
        self.ui.treeWidget.resizeColumnToContents(0)
        self.ui.treeWidget.resizeColumnToContents(1)


class LogsTab(FilesTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("logsTab")
        self.ui.saveButton.setText('Save Results && Logs')


class ResultsTab(FilesTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultsTab")
        self.ui.saveButton.setText('Save Results && Logs')


class ConfigTab(FilesTab):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("configTab")

