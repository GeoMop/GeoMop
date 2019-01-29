from PyQt5 import QtWidgets, QtCore, QtGui


class EditableLabel(QtWidgets.QGraphicsTextItem):
    def __init__(self, text, parent):
        super(EditableLabel, self).__init__(text, parent)
        self.setPos(QtCore.QPoint(5, 15))
        self.setDefaultTextColor(QtCore.Qt.white)
        self._editing = False
        self.document().contentsChanged.connect(self.make_text_fit_parent)
        self.make_text_fit_parent()

    def make_text_fit_parent(self):
        self.setTextWidth(self.parentItem().boundingRect().width() - 11)

    def editing(self, bool):
        self._editing = bool
        if bool:
            self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
            self.setDefaultTextColor(QtCore.Qt.black)
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
            self.setDefaultTextColor(QtCore.Qt.white)

    def mouseDoubleClickEvent(self, event):
        if self._editing:
            super(EditableLabel, self).mouseDoubleClickEvent(event)
        else:
            self.editing(True)

    def focusOutEvent(self, event):
        self.editing(False)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter or event.key() == QtCore.Qt.Key_Return:
            self.editing(False)
        else:
            super(EditableLabel, self).keyPressEvent(event)

    def paint(self, painter, style, widget):
        if self._editing:
            self.prepareGeometryChange()
            painter.setBrush(QtCore.Qt.white)
            painter.drawRect(self.boundingRect())

        super(EditableLabel, self).paint(painter, style, widget)



