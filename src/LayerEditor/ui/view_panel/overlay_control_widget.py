from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QDataStream, QIODevice
from PyQt5.QtWidgets import QListWidget

from LayerEditor.ui.view_panel.available_overalys_widget import AvailableOverlaysWidget


class OverlayControlWidget(QListWidget):
    def __init__(self, parent=None):
        super(OverlayControlWidget, self).__init__(parent)
        self.addItem("list test 1")
        self.addItem("list test 2")
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if isinstance(e.source(), AvailableOverlaysWidget):
            encoded = e.mimeData().data("application/x-qabstractitemmodeldatalist")
            stream = QDataStream(encoded, QIODevice.ReadOnly)
            r = stream.readInt()
            c = stream.readInt()
            v = stream.readQVariantMap()
            items = self.findItems(v[''], Qt.MatchExactly)
            for item in items:
                self.takeItem(self.row(item))
        else:
            e.setDropAction(Qt.MoveAction)
        super(OverlayControlWidget, self).dropEvent(e)




