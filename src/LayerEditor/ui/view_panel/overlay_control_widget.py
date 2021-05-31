from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QDataStream, QIODevice
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from LayerEditor.ui.view_panel.available_overalys_widget import AvailableOverlaysWidget


class OverlayControlWidget(QListWidget):
    def __init__(self, parent=None):
        super(OverlayControlWidget, self).__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if isinstance(e.source(), AvailableOverlaysWidget):
            available_overlay_item = self.parent().available_overlays.dragged_item
            items = self.findItems(available_overlay_item.get_full_name(), Qt.MatchExactly)
            for item in items:
                self.takeItem(self.row(item))
            index = self.indexAt(e.pos())
            drop_indicator_pos = self.dropIndicatorPosition()
            if drop_indicator_pos == self.BelowItem:
                row = index.row() + 1
            else:
                row = index.row()

            self.insertItem(row, QListWidgetItem(available_overlay_item.get_full_name()))
        else:
            e.setDropAction(Qt.MoveAction)
            super(OverlayControlWidget, self).dropEvent(e)




