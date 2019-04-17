from PyQt5 import QtGui
from PyQt5.QtCore import QEvent, QRect, QRectF, QMimeData, QPoint
from PyQt5.QtGui import QBrush, QColor, QPen, QDrag, QPixmap, QPainter, QIcon
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QStyleOptionGraphicsItem, \
    QPushButton, QLabel
from PyQt5.QtWidgets import QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt


class ToolboxView(QLabel):
    def __init__(self, item, parent):
        super(ToolboxView, self).__init__(parent)
        parent.addWidget(self)
        self.item = item
        rect = item.boundingRect()
        #rect.setTopLeft(rect.topLeft() + QPoint(-10,-10))
        #rect.setBottomRight(rect.bottomRight() + QPoint(10, 10))
        self.pixmap = QPixmap(rect.size().toSize())
        self.pixmap.fill(Qt.transparent)

        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.translate(-rect.topLeft())
        item.paint(painter, QStyleOptionGraphicsItem())
        for child in item.childItems():
            painter.save()
            painter.translate(child.mapToParent(item.pos()))
            child.paint(painter,QStyleOptionGraphicsItem(), None)
            painter.restore()

        painter.end()

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
        mime.setText("action")
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


