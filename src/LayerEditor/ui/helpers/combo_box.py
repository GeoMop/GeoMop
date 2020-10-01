from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QComboBox


class ComboBox(QComboBox):
    """QComboBox is staying in focus and is consuming key press events this subclass fixes it"""
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        event.ignore()
        if event.key() == QtCore.Qt.Key_Z and\
                event.modifiers() & QtCore.Qt.ControlModifier and\
                not event.modifiers() & QtCore.Qt.ShiftModifier:
            event.ignore()
        elif event.key() == QtCore.Qt.Key_Z and\
                event.modifiers() & QtCore.Qt.ControlModifier and\
                event.modifiers() & QtCore.Qt.ShiftModifier:
            event.ignore()
        
        super(ComboBox, self).keyPressEvent(event)

