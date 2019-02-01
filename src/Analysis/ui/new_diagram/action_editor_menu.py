"""
Definition of menu.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from PyQt5 import QtWidgets, QtCore, QtGui


class ActionEditorMenu(QtWidgets.QMenu):
    """Definition of menu containing editing options."""
    def __init__(self, parent):
        super(ActionEditorMenu, self).__init__(parent)
        self.setTitle("Edit")
        self.new_action = QtWidgets.QAction("New action")
        self.addAction(self.new_action)

        self.delete = QtWidgets.QAction("Delete")
        self.delete.setShortcut(QtGui.QKeySequence.Delete)
        self.addAction(self.delete)

