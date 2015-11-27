# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import datetime
import PyQt5.QtWidgets as QtWidgets
import time

from PyQt5 import QtCore


class Overview(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ["Id", "Name", "Insert Time", "Qued Time",
                        "Start Time", "Run Interval", "Status",
                        "Known Jobs", "Estimated Jobs", "Finished Jobs",
                        "Running Jobs"]
        self.time_format = "%d. %m. %y; %H:%M:%S"
        self.setObjectName("MultiJobOverview")
        self.setHeaderLabels(self.headers)
        self.setColumnHidden(0, True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)

    def resize_all_columns_to_contents(self):
        for idx, header in enumerate(self.headers):
            self.resizeColumnToContents(idx)

    @staticmethod
    def _update_item(item, state, time_format):
        # datetime.datetime.fromtimestamp(ts_epoch).strftime('%Y-%m-%d
        # %H:%M:%S') to remove time import
        item.setText(1, str(state.name))
        item.setText(2, time.strftime(
            time_format, time.gmtime(state.insert_time)))
        item.setText(3, time.strftime(
            time_format, time.gmtime(state.qued_time)))
        item.setText(4, time.strftime(
            time_format, time.gmtime(state.start_time)))
        item.setText(5, str(datetime.timedelta(seconds=state.run_interval)))
        item.setText(6, str(state.status.name))
        item.setText(7, str(state.known_jobs))
        item.setText(8, str(state.estimated_jobs))
        item.setText(9, str(state.finished_jobs))
        item.setText(10, str(state.running_jobs))
        return item

    def _get_item_by_key(self, key):
        for idx in range(0, self.topLevelItemCount()):
                item = self.topLevelItem(idx)
                if item.text(0) == key:
                    return idx, item
        return None

    def add_item(self, key, data):
        item = QtWidgets.QTreeWidgetItem(self)
        item.setTextAlignment(2, QtCore.Qt.AlignRight)
        item.setTextAlignment(3, QtCore.Qt.AlignRight)
        item.setTextAlignment(4, QtCore.Qt.AlignRight)
        item.setTextAlignment(5, QtCore.Qt.AlignRight)
        item.setTextAlignment(6, QtCore.Qt.AlignCenter)
        item.setTextAlignment(7, QtCore.Qt.AlignRight)
        item.setTextAlignment(8, QtCore.Qt.AlignRight)
        item.setTextAlignment(9, QtCore.Qt.AlignRight)
        item.setTextAlignment(10, QtCore.Qt.AlignRight)
        item.setText(0, key)
        return self._update_item(item, data, self.time_format)

    def update_item(self, key, data):
        index, item = self._get_item_by_key(key)
        if item:
            self._update_item(item, data, self.time_format)
        self.resize_all_columns_to_contents()

    def remove_item(self, key):
        index, item = self._get_item_by_key(key)
        return self.takeTopLevelItem(index)

    def reload_items(self, data):
        self.clear()
        if data:
            for key in data:
                state = data[key]["state"]
                self.add_item(key, state)
        self.resize_all_columns_to_contents()

