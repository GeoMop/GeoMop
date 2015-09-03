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
        self.setHeaderLabels(["Name", "Insert Time", "Run Time",
                              "Run Interval", "Status"])

    def set_data(self, data):
        # clear data
        self.clear()
        if data:
        # populate with data
            for row_id, row in enumerate(data):
                QtWidgets.QTreeWidgetItem(self)
                for col_id, item in enumerate(row[1:]):
                    self.topLevelItem(row_id).setText(col_id, str(item))

