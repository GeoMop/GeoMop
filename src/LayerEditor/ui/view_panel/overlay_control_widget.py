from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from LayerEditor.ui.view_panel.available_overalys_widget import AvailableOverlaysWidget
from LayerEditor.ui.view_panel.overlay_list_item import OverlayListItem


class OverlayControlWidget(QListWidget):
    overlay_inserted = pyqtSignal(object, float)   # data_object, row, opacity
    overlay_removed = pyqtSignal(object)
    def __init__(self, parent=None):
        super(OverlayControlWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if isinstance(e.source(), AvailableOverlaysWidget):
            available_overlay_item = self.parent().available_overlays.dragged_item
            items = self.findItems(available_overlay_item.data_item.overlay_name, Qt.MatchExactly)
            row = self.get_drop_index(e)
            opacity = 1
            for item in items:
                if row < self.row(item):
                    row -= 1
                self.overlay_removed.emit(item.data_item)
                self.takeItem(self.row(item))
                opacity = item.opacity

            self.overlay_inserted.emit(available_overlay_item.data_item, opacity)
            self.insertItem(row, OverlayListItem(available_overlay_item.data_item, opacity))
        else:
            e.setDropAction(Qt.MoveAction)
            super(OverlayControlWidget, self).dropEvent(e)
            if e.isAccepted():
                item = self.currentItem()
                self.overlay_removed.emit(item.data_item)
                self.overlay_inserted.emit(item.data_item, item.opacity)

    def get_drop_index(self, drop_event):
        index = self.indexAt(drop_event.pos())
        drop_indicator_pos = self.dropIndicatorPosition()
        if drop_indicator_pos == self.BelowItem:
            row = index.row() + 1
        else:
            row = index.row()
        if row == -1:
            return self.count()
        else:
            return row

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == Qt.Key_Delete or e.key() == Qt.Key_Backspace:
            self.overlay_removed.emit(self.currentItem().data_item)
            self.takeItem(self.currentRow())

    def focusInEvent(self, e: QtGui.QFocusEvent) -> None:
        super(OverlayControlWidget, self).focusInEvent(e)
        self.grabKeyboard()

    def focusOutEvent(self, e: QtGui.QFocusEvent) -> None:
        super(OverlayControlWidget, self).focusOutEvent(e)
        self.releaseKeyboard()


