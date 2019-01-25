"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
import abc
from .node import Node
from .node_editor_menu import NodeEditorMenu
from .connection import Connection


class Workspace(QtWidgets.QGraphicsView):

    def __init__(self, parent=None):
        super(Workspace, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self.edit_menu = self.parent().edit_menu
        self.edit_menu.new_node.triggered.connect(self.add_node)
        self.edit_menu.delete.triggered.connect(self.delete_items)
        self.new_node_pos = QtCore.QPoint()
        self.setMouseTracking(True)
        self.nodes = []
        self.connections = []
        self.new_connection = None
        self.setDragMode(self.RubberBandDrag)

        # settings for zooming the workspace
        self.zoom = 1.0
        self.max_zoom = 10.0
        self.min_zoom = 0.1
        self.zoom_factor = 1.2

    def wheelEvent(self, event):
        degrees = event.angleDelta() / 8
        steps = degrees.y() / 15

        if steps > 0:
            self.zoom = min(self.max_zoom, self.zoom * self.zoom_factor)

        else:
            self.zoom = max(self.min_zoom, self.zoom / self.zoom_factor)

        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setTransform(QtGui.QTransform().scale(self.zoom, self.zoom))

    def contextMenuEvent(self, event):
        self.new_node_pos = self.mapToScene(event.pos())
        self.edit_menu.exec_(event.globalPos())

    def add_node(self):
        self.nodes.append(Node(None, self.new_node_pos))
        self.scene.addItem(self.nodes[-1])

    def add_connection(self, port):
        if self.new_connection is None:
            self.new_connection = Connection(port)
            self.scene.addItem(self.new_connection)
        else:
            self.new_connection.set_port2(port)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)
            self.connections.append(self.new_connection)
            self.new_connection = None

    def mouseMoveEvent(self, event):
        super(Workspace, self).mouseMoveEvent(event)
        if self.new_connection is not None:
            self.new_connection.set_port2_pos(self.mapToScene(event.pos()))

    def delete_items(self):
        for item in self.scene.selectedItems():
            if item.is_node():
                conn_to_delete = []
                for conn in self.connections:
                    for port in item.ports():
                        if conn.is_connected(port):
                            try:
                                conn_to_delete.append(conn)
                            except:
                                print("Tried to delete connection again... probably...")

                for conn in conn_to_delete:
                    self.delete_connection(conn)
                self.delete_node(item)
            else:
                pass
                self.delete_connection(item)

    def delete_node(self, node):
        self.nodes.remove(node)
        self.scene.removeItem(node)

    def delete_connection(self, conn):
        self.connections.remove(conn)
        self.scene.removeItem(conn)




