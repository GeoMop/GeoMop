from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, QRectF, QPointF


class ResizeHandle(QtWidgets.QGraphicsRectItem):
    top_left = 1
    top_middle = 2
    top_right = 4
    middle_left = 8
    middle_right = 16
    bottom_left = 32
    bottom_middle = 64
    bottom_right = 128

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
        top_left: lambda w, cs, rect: QRectF(rect.left(), rect.top(), cs, cs),
        top_middle: lambda w, cs, rect: QRectF(rect.left() + cs, rect.top(), rect.width() - 2 * cs, w),
        top_right: lambda w, cs, rect: QRectF(rect.right() - cs, rect.top(), cs, cs),
        middle_left: lambda w, cs, rect: QRectF(rect.left(), rect.top() + cs, w, rect.height() - 2 * cs),
        middle_right: lambda w, cs, rect: QRectF(rect.right() - w, rect.top() + cs, w, rect.height() - 2 * cs),
        bottom_left: lambda w, cs, rect: QRectF(rect.left(), rect.bottom() - cs, cs, cs),
        bottom_middle: lambda w, cs, rect: QRectF(rect.left() + cs, rect.bottom() - w, rect.width() - 2 * cs, w),
        bottom_right: lambda w, cs, rect: QRectF(rect.right() - cs, rect.bottom() - cs, cs, cs),
    }

    def __init__(self, resize_handler, parent_item, width, dock, corner_size=None, corners=True):
        super(ResizeHandle, self).__init__(parent_item)
        self.corner_size = corner_size if corner_size is not None else width
        self.corners = corners
        self.setZValue(0.5)
        self.resize_handler = resize_handler
        self.width = width
        self.dock = dock
        self.setAcceptHoverEvents(True)
        self.pressed = False
        self.setRect(self.get_rect())
        self.setPen(QtGui.QPen(Qt.NoPen))
        self.setFlag(self.ItemHasNoContents)

    def get_rect(self):
        return self.get_handle_rect[self.dock](self.width, self.corner_size if self.corners else 0,
                                               self.parentItem().boundingRect())

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
        self.setRect(self.get_rect())

    def mousePressEvent(self, press_event):
        if self.parentItem().isSelected():
            self.pressed = True
        else:
            super(ResizeHandle, self).mousePressEvent(press_event)

    def mouseMoveEvent(self, move_event):
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

    def mouseReleaseEvent(self, release_event):
        super(ResizeHandle, self).mouseReleaseEvent(release_event)
        self.parentItem().height_has_changed()
        self.parentItem().width_has_changed()

