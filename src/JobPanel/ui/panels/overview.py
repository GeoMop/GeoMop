# -*- coding: utf-8 -*-
"""
Table of MultiJobs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import datetime
import PyQt5.QtWidgets as QtWidgets
from PyQt5 import QtCore, QtGui

from JobPanel.data import TaskStatus
from ..menus.main_menu_bar import MultiJobMenu

ERROR_BRUSH = QtGui.QBrush(QtGui.QColor(255, 0, 0, 40))


class Overview(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headers = ["Id", "Analysis", "Name", "Insert Time", "Queued Time",
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
        self.header().resizeSection(3, 120)
        self.header().resizeSection(4, 120)
        self.header().resizeSection(5, 120)
        self.header().resizeSection(6, 80)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAllColumnsShowFocus(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)


    @staticmethod
    def _update_item(item, state, time_format):
        item.setText(1, str(state.analysis))
        item.setText(2, str(state.name))
        item.setText(3, datetime.datetime.fromtimestamp(
                state.insert_time).strftime(time_format))
        if state.queued_time:
            item.setText(4, datetime.datetime.fromtimestamp(
                state.queued_time).strftime(time_format))
        else:
            item.setText(4, "Not Queued Yet")
        if state.start_time:
            item.setText(5, datetime.datetime.fromtimestamp(
                state.start_time).strftime(time_format))
        else:
            item.setText(5, "Not Started Yet")
        item.setText(6, str(datetime.timedelta(seconds=int(state.run_interval))))
        item.setText(7, str(state.status))
        item.setText(8, str(state.known_jobs))
        item.setText(9, str(state.estimated_jobs))
        item.setText(10, str(state.finished_jobs))
        item.setText(11, str(state.running_jobs))

        # background color
        if state.status == TaskStatus.error:
            for i in range(item.columnCount()):
                item.setBackground(i, ERROR_BRUSH)

        return item

    def _get_item_by_key(self, key):
        for idx in range(0, self.topLevelItemCount()):
                item = self.topLevelItem(idx)
                if item.text(0) == key:
                    return idx, item
        return None

    def _open_context_menu(self, position):
        if self.itemAt(position) is None:
            self.clearSelection()
        contextMenu = self.parentWidget().parentWidget().findChild(MultiJobMenu,"multiJobMenu")
        contextMenu.popup(self.viewport().mapToGlobal(position))

    def add_item(self, key, data):
        item = QtWidgets.QTreeWidgetItem(self)
        item.setTextAlignment(3, QtCore.Qt.AlignRight)
        item.setTextAlignment(4, QtCore.Qt.AlignRight)
        item.setTextAlignment(5, QtCore.Qt.AlignRight)
        item.setTextAlignment(6, QtCore.Qt.AlignRight)
        item.setTextAlignment(7, QtCore.Qt.AlignCenter)
        item.setTextAlignment(8, QtCore.Qt.AlignRight)
        item.setTextAlignment(9, QtCore.Qt.AlignRight)
        item.setTextAlignment(10, QtCore.Qt.AlignRight)
        item.setTextAlignment(11, QtCore.Qt.AlignRight)
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
        current_id = None
        if self.currentItem() is not None:
            current_id = self.currentItem().text(0)

        selection_ids = []
        for sel_item in self.selectedItems():
            selection_ids.append(sel_item.text(0))
        self.reset()
        self.clear()
        if data:
            for key in data:
                if data[key].valid:
                    self.add_item(key, data[key].state)

        if current_id is not None:
            if self._get_item_by_key(current_id) is not None:
                self.setCurrentItem(self._get_item_by_key(current_id)[1], 1)

        for mj_id in selection_ids:
            item = self._get_item_by_key(mj_id)
            if item is not None:
                item[1].setSelected(True)
        self.resizeColumnToContents(1)
