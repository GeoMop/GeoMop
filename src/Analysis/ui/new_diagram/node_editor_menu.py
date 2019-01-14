"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets


class NodeEditorMenu(QtWidgets.QMenu):
    def __init__(self, parent):
        super(NodeEditorMenu, self).__init__(parent)
        self.new_node = QtWidgets.QAction("New node")


        self.addAction(self.new_node)

