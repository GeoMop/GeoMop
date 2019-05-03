from PyQt5 import QtWidgets, QtCore, QtGui
from .g_port import GPort


class EditableLabel(QtWidgets.QGraphicsTextItem):
    def __init__(self, text, parent):
        super(EditableLabel, self).__init__(text, parent)
        self.setPos(QtCore.QPoint(parent.resize_handle_width, GPort.SIZE / 2 + parent.type_name.boundingRect().height()))
        self.setDefaultTextColor(QtCore.Qt.black)
        self._editing = False
        self.start_text = ""
        self.document().contentsChanged.connect(self.parentItem().name_change)
        self.setAcceptHoverEvents(False)

    def editing(self, bool):
        if self._editing != bool:
            self._editing = bool
            if bool:
                self.start_text = self.toPlainText()
                self.setTextWidth(-1)
                self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
                self.setFocus(QtCore.Qt.MouseFocusReason)
                self.setSelected(True)
                cursor = self.textCursor()
                cursor.select(QtGui.QTextCursor.Document)
                self.setTextCursor(cursor)
            else:
                if self.parentItem().name_has_changed() or self.start_text == self.toPlainText():
                    cursor = self.textCursor()
                    cursor.clearSelection()
                    self.setTextCursor(cursor)
                    self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
                    if not len(self.toPlainText()):
                        self.setTextWidth(self.parentItem().inner_area().width())
                else:
                    msg1 = "Object name has to be unique and at least one character long!"
                    msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                                "Duplicate object name", msg1,
                                                QtWidgets.QMessageBox.Ok)
                    msg.exec_()
                    self._editing = True
                    self.setFocus(QtCore.Qt.MouseFocusReason)
                    self.setSelected(True)

    def mouseDoubleClickEvent(self, event):
        if self._editing:
            super(EditableLabel, self).mouseDoubleClickEvent(event)
        else:
            self.editing(True)

    def focusOutEvent(self, event):
        super(EditableLabel, self).focusOutEvent(event)
        if event.reason() != QtCore.Qt.ActiveWindowFocusReason:
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



