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


BLACK_BRUSH = QtGui.QBrush(QtCore.Qt.black)
WHITE_BRUSH = QtGui.QBrush(QtCore.Qt.white)

ONLINE_BRUSH = QtGui.QBrush(QtCore.Qt.darkGreen)
OFFLINE_BRUSH = QtGui.QBrush(QtCore.Qt.darkRed)

TASK_STATUS_BRUSHES = {
    TaskStatus.error: QtGui.QBrush(QtGui.QColor(255, 0, 0, 40)),
    TaskStatus.finished: QtGui.QBrush(QtGui.QColor(0, 255, 0, 40)),
    TaskStatus.running: QtGui.QBrush(QtGui.QColor(0, 0, 255, 40)),
    TaskStatus.stopped: QtGui.QBrush(QtGui.QColor(255, 102, 0, 40)),
    TaskStatus.queued: QtGui.QBrush(QtGui.QColor(128, 128, 128, 40))}


class Overview(QtWidgets.QTreeWidget):
    def __init__(self, parent=None, frontend_service=None):
        super().__init__(parent)

        self.frontend_service = frontend_service

        self.headers = ["Id", "Analysis", "Name", "Queued",
                        "Start", "Wall", "Status", "Data", "Jobs"]
        self.time_format = "%X %d %b"
        self.setObjectName("MultiJobOverview")
        self.setHeaderLabels(self.headers)
        self.setColumnHidden(0, True)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)
        self.header().resizeSection(3, 160)
        self.header().resizeSection(4, 160)
        self.header().resizeSection(5, 120)
        self.header().resizeSection(6, 120)
        self.header().resizeSection(7, 120)
        self.header().resizeSection(8, 120)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAllColumnsShowFocus(True)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._open_context_menu)

    def _update_item(self, item, data):
        key = item.text(0)
        state = data[key].state
        item.setText(1, str(state.analysis))
        item.setText(2, str(state.name))
        # item.setText(3, datetime.datetime.fromtimestamp(
        #         state.insert_time).strftime(self.time_format))
        if state.queued_time:
            item.setText(3, datetime.datetime.fromtimestamp(
                state.queued_time).strftime(self.time_format))
        else:
            item.setText(3, "Not Queued Yet")
        if state.start_time:
            item.setText(4, datetime.datetime.fromtimestamp(
                state.start_time).strftime(self.time_format))
        else:
            item.setText(4, "Not Started Yet")
        item.setText(5, str(datetime.timedelta(seconds=int(state.run_interval))))
        item.setText(6, str(state.status))
        if data[key].preset.mj_ssh_preset is not None:
            if data[key].preset.downloaded:
                item.setText(7, "Downloaded")
            else:
                item.setText(7, "Remote")
        else:
            item.setText(7, "Local")
        item.setText(8, "{}, {}, {}".format(state.known_jobs, state.running_jobs, state.finished_jobs))

        # background color
        if state.status in TASK_STATUS_BRUSHES:
            brush = TASK_STATUS_BRUSHES[state.status]
        else:
            brush = WHITE_BRUSH
        for i in range(item.columnCount()):
            item.setBackground(i, brush)

        # status color
        mj_delegator_online = self.frontend_service.get_mj_delegator_online()
        if data[key].preset.deleted_remote:
            item.setForeground(6, BLACK_BRUSH)
        else:
            if self.frontend_service.get_backend_status() and \
                    key in mj_delegator_online and mj_delegator_online[key]:
                item.setForeground(6, ONLINE_BRUSH)
            else:
                item.setForeground(6, OFFLINE_BRUSH)

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
        item.setTextAlignment(6, QtCore.Qt.AlignCenter)
        item.setTextAlignment(7, QtCore.Qt.AlignCenter)
        item.setText(0, key)
        item.setToolTip(8, "known, running, finished")
        return self._update_item(item, data)

    def update_item(self, key, data):
        index, item = self._get_item_by_key(key)
        if item:
            self._update_item(item, data)
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
                    self.add_item(key, data)

        if current_id is not None:
            if self._get_item_by_key(current_id) is not None:
                self.setCurrentItem(self._get_item_by_key(current_id)[1], 1)

        for mj_id in selection_ids:
            item = self._get_item_by_key(mj_id)
            if item is not None:
                item[1].setSelected(True)
        self.resizeColumnToContents(1)
