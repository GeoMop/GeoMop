# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class MultiJobOverview(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(MultiJobOverview, self).__init__(parent)
        self.ui = UiMultiJobOverview()
        self.ui.setup_ui(self)
        self.show()


class UiMultiJobOverview(object):

    def setup_ui(self, tree_widget):
        tree_widget.setObjectName("MultiJobOverview")
        tree_widget.headerItem().setText(0, "Name")
        tree_widget.headerItem().setText(1, "Inserted time")
        tree_widget.headerItem().setText(2, "Run Time")
        tree_widget.headerItem().setText(3, "Run Interval")
        tree_widget.headerItem().setText(4, "Status")

        item_0 = QtWidgets.QTreeWidgetItem(tree_widget)
        tree_widget.topLevelItem(0).setText(0, "MultiJob01")
        tree_widget.topLevelItem(0).setText(1, "Now")
        tree_widget.topLevelItem(0).setText(2, "For several hours")
        tree_widget.topLevelItem(0).setText(3, "1 day")
        tree_widget.topLevelItem(0).setText(4, "Running")

        item_1 = QtWidgets.QTreeWidgetItem(tree_widget)
        tree_widget.topLevelItem(1).setText(0, "MultiJob02")
        tree_widget.topLevelItem(1).setText(1, "Now")
        tree_widget.topLevelItem(1).setText(2, "For several hours")
        tree_widget.topLevelItem(1).setText(3, "2 day")
        tree_widget.topLevelItem(1).setText(4, "Running")