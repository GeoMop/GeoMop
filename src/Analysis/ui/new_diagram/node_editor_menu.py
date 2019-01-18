"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui


class NodeEditorMenu(QtWidgets.QMenu):
    def __init__(self, parent):
        super(NodeEditorMenu, self).__init__(parent)
        self.setTitle("Edit")
        self.new_node = QtWidgets.QAction("New node")
        self.addAction(self.new_node)

        self.delete = QtWidgets.QAction("Delete")
        self.delete.setShortcut(QtGui.QKeySequence.Delete)
        self.addAction(self.delete)

