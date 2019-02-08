from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRectF, QPointF

class ResizeHandle(QtWidgets.QGraphicsRectItem):
    top_left = 1
    top_middle = 2
    top_right = 3
    middle_left = 4
    middle_right = 5
    bottom_left = 6
    bottom_middle = 7
    bottom_right = 8

    cursors = {
        top_left: Qt.SizeFDiagCursor,
        top_middle: Qt.SizeVerCursor,
        top_right: Qt.SizeBDiagCursor,
        middle_left: Qt.SizeHorCursor,
        middle_right: Qt.SizeHorCursor,
        bottom_left: Qt.SizeBDiagCursor,
        bottom_middle: Qt.SizeVerCursor,
        bottom_right: Qt.SizeFDiagCursor
    }
    
    get_handle_rect = {
        top_left: lambda w, rect: QRectF(rect.left(), rect.top(), w, w),
        top_middle: lambda w, rect: QRectF(rect.left() + w, rect.top(), rect.width() - 2 * w, w),
        top_right: lambda w, rect: QRectF(rect.right() - w, rect.top(), w, w),
        middle_left: lambda w, rect: QRectF(rect.left(), rect.top() + w, w, rect.height() - 2 * w),
        middle_right: lambda w, rect: QRectF(rect.right() - w, rect.top() + w, w, rect.height() - 2 * w),
        bottom_left: lambda w, rect: QRectF(rect.left(), rect.bottom() - w, w, w),
        bottom_middle: lambda w, rect: QRectF(rect.left() + w, rect.bottom() - w, rect.width() - 2 * w, w),
        bottom_right: lambda w, rect: QRectF(rect.right() - w, rect.bottom() - w, w, w),
    }

    def __init__(self, resize_handler, parent, width, dock):
        super(ResizeHandle, self).__init__(parent)
        self.setZValue(0.5)
        self.resize_handler = resize_handler
        self.width = width
        self.dock = dock
        self.setAcceptHoverEvents(True)
        self.pressed = False
        self.setRect(self.get_handle_rect[dock](width, parent.boundingRect()))
        self.setPen(QtGui.QPen(Qt.NoPen))
        self.setFlag(self.ItemHasNoContents)

    def hoverMoveEvent(self, move_event):
        """Executed when the mouse moves over the shape (NOT PRESSED)."""
        if self.parentItem().isSelected():
            self.setCursor(self.cursors[self.dock])
        super().hoverMoveEvent(move_event)

    def hoverLeaveEvent(self, move_event):
        """Executed when the mouse leaves the shape (NOT PRESSED)."""
        self.setCursor(Qt.ArrowCursor)
        super().hoverLeaveEvent(move_event)

    def update_handle(self):
        self.setRect(self.get_handle_rect[self.dock](self.width, self.parentItem().boundingRect()))

    def mousePressEvent(self, press_event):
        if self.parentItem().isSelected():
            self.pressed = True
        else:
            super(ResizeHandle, self).mousePressEvent(press_event)

    def mouseMoveEvent(self, move_event):
        print("move mouse resize")
        move = move_event.pos() - move_event.lastPos()
        if self.pressed:
            self.parentItem().prepareGeometryChange()

            if self.dock == self.top_left:
                old_width = self.parentItem().width
                old_height = self.parentItem().height
                self.parentItem().width -= move.x()
                self.parentItem().height -= move.y()
                self.parentItem().moveBy(old_width - self.parentItem().width, old_height - self.parentItem().height)

            elif self.dock == self.top_middle:
                old_height = self.parentItem().height
                self.parentItem().height -= move.y()
                self.parentItem().moveBy(0, old_height - self.parentItem().height)

            elif self.dock == self.top_right:
                old_height = self.parentItem().height
                self.parentItem().width += move.x()
                self.parentItem().height -= move.y()
                self.parentItem().moveBy(0, old_height - self.parentItem().height)

            elif self.dock == self.middle_left:
                old_width = self.parentItem().width
                self.parentItem().width -= move.x()
                self.parentItem().moveBy(old_width - self.parentItem().width, 0)

            elif self.dock == self.middle_right:
                self.parentItem().width += move.x()

            elif self.dock == self.bottom_left:
                old_width = self.parentItem().width
                self.parentItem().width -= move.x()
                self.parentItem().height += move.y()
                self.parentItem().moveBy(old_width - self.parentItem().width, 0)

            elif self.dock == self.bottom_middle:
                self.parentItem().height += move.y()

            elif self.dock == self.bottom_right:
                self.parentItem().width += move.x()
                self.parentItem().height += move.y()


