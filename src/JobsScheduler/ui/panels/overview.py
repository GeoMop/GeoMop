# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import datetime
import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtCore


class Overview(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ["Id", "Name", "Insert Time", "Queued Time",
                        "Start Time", "Run Interval", "Status",
                        "Known Jobs", "Estimated Jobs", "Finished Jobs",
                        "Running Jobs"]
        self.time_format = "%X %x"
        self.setObjectName("MultiJobOverview")
        self.setHeaderLabels(self.headers)
        self.setColumnHidden(0, True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)
        self.header().resizeSection(2, 120)
        self.header().resizeSection(3, 120)
        self.header().resizeSection(4, 120)

    @staticmethod
    def _update_item(item, state, time_format):
        item.setText(1, str(state.name))
        item.setText(2, datetime.datetime.fromtimestamp(
                state.insert_time).strftime(time_format))
        if state.queued_time:
            item.setText(3, datetime.datetime.fromtimestamp(
                state.queued_time).strftime(time_format))
        else:
            item.setText(3, "Not Queued Yet")
        if state.start_time:
            item.setText(4, datetime.datetime.fromtimestamp(
                state.start_time).strftime(time_format))
        else:
            item.setText(4, "Not Started Yet")
        item.setText(5, str(datetime.timedelta(seconds=state.run_interval)))
        item.setText(6, str(state.status))
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
        self.resizeColumnToContents(1)

    def remove_item(self, key):
        index, item = self._get_item_by_key(key)
        return self.takeTopLevelItem(index)

    def reload_items(self, data):
        self.clear()
        if data:
            for key in data:
                self.add_item(key, data[key].state)
        self.setCurrentItem(self.topLevelItem(0))
        self.resizeColumnToContents(1)

