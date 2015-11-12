# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import PyQt5.QtWidgets as QtWidgets


class Overview(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(Overview, self).__init__(parent)
        self.headers = ["Id", "Name", "Insert Time", "Run Time",
                        "Run Interval", "Status"]
        self.keys = ["name", "insert_time", "run_time", "run_interval",
                     "status"]
        self.setObjectName("MultiJobOverview")
        self.setHeaderLabels(self.headers)
        self.setColumnHidden(0, True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)

    def reload_view(self, data):
        self.clear()
        if data:
            for key in data:
                row = QtWidgets.QTreeWidgetItem(self)
                row.setText(0, str(key))
                for col_id, item_key in enumerate(self.keys):
                    row.setText(col_id + 1, str(data[key]["state"][item_key]))
