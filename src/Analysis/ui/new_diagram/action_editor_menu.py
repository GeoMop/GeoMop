"""
Definition of menu.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
from PyQt5 import QtWidgets, QtCore, QtGui


class ActionEditorMenu(QtWidgets.QMenu):
    """Definition of menu containing editing options."""
    def __init__(self, parent=None):
        super(ActionEditorMenu, self).__init__(parent)
        self.setTitle("Edit")
        self.new_action = QtWidgets.QAction("New action")
        self.addAction(self.new_action)

        self.delete = QtWidgets.QAction("Delete")
        self.delete.setShortcut(QtGui.QKeySequence.Delete)
        self.addAction(self.delete)

        self.add_random = QtWidgets.QAction("Add random action (for test purposes)")
        self.addAction(self.add_random)

        self.add_while = QtWidgets.QAction("Add while loop")
        self.addAction(self.add_while)

        self.order = QtWidgets.QAction("Arrange diagram")
        self.addAction(self.order)
