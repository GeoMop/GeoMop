from PyQt5 import QtWidgets, QtCore, QtGui
from node import Node
from node_editor_menu import NodeEditorMenu
from connection import Connection


class Workspace(QtWidgets.QGraphicsView):
    def __init__(self, parent=None):
        super(Workspace, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self.menu = NodeEditorMenu(self)
        self.menu.new_node.triggered.connect(self.add_node)
        self.new_node_pos = QtCore.QPoint()
        self.setMouseTracking(True)
        self.nodes = []
        self.connections = []
        self.new_connection = None

    def contextMenuEvent(self, event):
        self.new_node_pos = self.mapToScene(event.pos())
        self.menu.exec_(event.globalPos())

    def add_node(self):
        item = Node(None, self.new_node_pos)
        self.scene.addItem(item)

    def add_connection(self, port):
        if self.new_connection is None:
            self.new_connection = Connection(port)
            self.scene.addItem(self.new_connection)
        else:
            self.new_connection.set_port2(port)
            self.connections.append(self.new_connection)
            self.new_connection = None


    def mouseMoveEvent(self, event):
        super(Workspace, self).mouseMoveEvent(event)
        if self.new_connection is not None:
            self.new_connection.set_port2_pos(self.mapToScene(event.pos()))
        self.scene.update()


