# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class MultiJobInfoTab(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(MultiJobInfoTab, self).__init__(parent)
        self.ui = UiMultiJobInfoTab()
        self.ui.setup_ui(self)
        self.show()


class UiMultiJobInfoTab(object):

    def setup_ui(self, tab_widget):
        tab_widget.setObjectName("MultiJobInfoTab")

        # overview tab
        self.overview_tab = QtWidgets.QWidget()
        self.overview_tab.setObjectName("overviewTab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.overview_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.overviewTreeWidget = QtWidgets.QTreeWidget(self.overview_tab)
        self.overviewTreeWidget.setObjectName("overviewTreeWidget")
        self.overviewTreeWidget.headerItem().setText(0, "Name")
        self.overviewTreeWidget.headerItem().setText(1, "Inserted time")
        self.overviewTreeWidget.headerItem().setText(2, "Run Time")
        self.overviewTreeWidget.headerItem().setText(3, "Run Interval")
        self.overviewTreeWidget.headerItem().setText(4, "Status")

        item_0 = QtWidgets.QTreeWidgetItem(self.overviewTreeWidget)
        self.overviewTreeWidget.topLevelItem(0).setText(0, "MultiJob01")
        self.overviewTreeWidget.topLevelItem(0).setText(1, "Now")
        self.overviewTreeWidget.topLevelItem(0).setText(2, "For several hours")
        self.overviewTreeWidget.topLevelItem(0).setText(3, "1 day")
        self.overviewTreeWidget.topLevelItem(0).setText(4, "Running")
        self.horizontalLayout.addWidget(self.overviewTreeWidget)
        tab_widget.addTab(self.overview_tab, "Overview")
        
        # job tab
        self.job_tab = QtWidgets.QWidget()
        self.job_tab.setObjectName("overviewTab")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.job_tab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.jobTreeWidget = QtWidgets.QTreeWidget(self.job_tab)
        self.jobTreeWidget.setObjectName("jobTreeWidget")
        self.jobTreeWidget.headerItem().setText(0, "Name")
        self.jobTreeWidget.headerItem().setText(1, "Inserted time")
        self.jobTreeWidget.headerItem().setText(2, "Run Time")
        self.jobTreeWidget.headerItem().setText(3, "Run Interval")
        self.jobTreeWidget.headerItem().setText(4, "Status")

        item_0 = QtWidgets.QTreeWidgetItem(self.jobTreeWidget)
        self.jobTreeWidget.topLevelItem(0).setText(0, "Job01")
        self.jobTreeWidget.topLevelItem(0).setText(1, "Now")
        self.jobTreeWidget.topLevelItem(0).setText(2, "For several hours")
        self.jobTreeWidget.topLevelItem(0).setText(3, "1 day")
        self.jobTreeWidget.topLevelItem(0).setText(4, "Running")
        self.horizontalLayout.addWidget(self.jobTreeWidget)
        tab_widget.addTab(self.job_tab, "Overview")
