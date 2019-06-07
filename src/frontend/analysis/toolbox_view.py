from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, QRect, QRectF, QMimeData, QPoint
from PyQt5.QtGui import QBrush, QColor, QPen, QDrag, QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QStyleOptionGraphicsItem, \
    QPushButton, QLabel
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt

from .g_action_background import ActionStatus


class ToolboxView(QLabel):
    def __init__(self, item, parent):
        super(ToolboxView, self).__init__(parent)
        parent.addWidget(self)
        self.item = item
        self.pixmap = item.paint_pixmap()

        self.selected = False
        self.setPixmap(self.pixmap)

    def get_pos_correction(self):
        return QPoint(self.item.width/2, self.item.height/2)

    def mousePressEvent(self, press_event):
        parent = self.parent()
        for item in parent.items:
            item.deselect()
        self.selected = True
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(self.item.w_data_item.action_name)
        drag.setMimeData(mime)
        drag.setPixmap(self.pixmap)
        drag.setHotSpot(QPoint( drag.pixmap().width()/2,
                                drag.pixmap().height()/2))
        ret = drag.exec(Qt.MoveAction)

    def deselect(self):
        if self.selected:
            self.selected = False

    def enterEvent(self, *args, **kwargs):
        super(ToolboxView, self).enterEvent(*args, **kwargs)
        self.setCursor(Qt.OpenHandCursor)

    def leaveEvent(self, *args, **kwargs):
        super(ToolboxView, self).leaveEvent(*args, **kwargs)
        self.setCursor(Qt.ArrowCursor)


