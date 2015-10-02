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
        self.setObjectName("MultiJobOverview")
        self.setHeaderLabels(["Id", "Name", "Insert Time", "Run Time",
                              "Run Interval", "Status"])
        self.setColumnHidden(0, True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)

    def reload_view(self, data):
        self.clear()
        if data:
            for key in data:
                row = QtWidgets.QTreeWidgetItem(self)
                row.setText(0, str(key))
                for col_id, item in enumerate(data[key][0:2]):
                    row.setText(col_id + 1, str(item))

