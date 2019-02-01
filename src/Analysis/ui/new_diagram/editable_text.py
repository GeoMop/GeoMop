from PyQt5 import QtWidgets, QtCore, QtGui
from .port import Port


class EditableLabel(QtWidgets.QGraphicsTextItem):
    def __init__(self, text, parent):
        super(EditableLabel, self).__init__(text, parent)
        self.setPos(QtCore.QPoint(parent.resize_handle_width, Port.SIZE / 2))
        self.setDefaultTextColor(QtCore.Qt.black)
        self._editing = False
        self.document().contentsChanged.connect(self.parentItem().position_ports)
        self.setAcceptHoverEvents(False)

    def editing(self, bool):
        self._editing = bool
        if bool:
            self.setTextWidth(-1)
            self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
            self.setFocus(QtCore.Qt.MouseFocusReason)
            self.setSelected(True)
            cursor = self.textCursor()
            cursor.select(QtGui.QTextCursor.Document)
            self.setTextCursor(cursor)
        else:
            cursor = self.textCursor()
            cursor.clearSelection()
            self.setTextCursor(cursor)
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            if not len(self.toPlainText()):
                self.setTextWidth(self.parentItem().inner_area().width())

    def mouseDoubleClickEvent(self, event):
        if self._editing:
            super(EditableLabel, self).mouseDoubleClickEvent(event)
        else:
            self.editing(True)

    def focusOutEvent(self, event):
        super(EditableLabel, self).focusOutEvent(event)
        self.editing(False)

    def width(self):
        return self.boundingRect().width() if len(self.toPlainText()) else 0

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.editing(False)
        else:
            super(EditableLabel, self).keyPressEvent(event)

    def paint(self, painter, style, widget):
        if self._editing:
            self.prepareGeometryChange()

        super(EditableLabel, self).paint(painter, style, widget)



