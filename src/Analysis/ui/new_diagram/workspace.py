"""
Start script that initializes main window and runs APP
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui
from .action import Action
from .connection import Connection


class Workspace(QtWidgets.QGraphicsView):

    def __init__(self, parent=None):
        super(Workspace, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self.edit_menu = self.parent().edit_menu
        self.edit_menu.new_action.triggered.connect(self.add_action)
        self.edit_menu.delete.triggered.connect(self.delete_items)
        self.new_action_pos = QtCore.QPoint()
        self.setMouseTracking(True)
        self.actions = []
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
        self.new_action_pos = self.mapToScene(event.pos())
        self.edit_menu.exec_(event.globalPos())

    def add_action(self):
        self.actions.append(Action(None, self.new_action_pos))
        self.scene.addItem(self.actions[-1])

    def add_connection(self, port):
        if self.new_connection is None:
            self.new_connection = Connection(port)
            self.scene.addItem(self.new_connection)
            port.connections.append(self.new_connection)
        else:
            self.new_connection.set_port2(port)
            port.connections.append(self.new_connection)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)
            self.connections.append(self.new_connection)
            self.new_connection = None

    def mouseMoveEvent(self, event):
        super(Workspace, self).mouseMoveEvent(event)
        if self.new_connection is not None:
            self.new_connection.set_port2_pos(self.mapToScene(event.pos()))

    def delete_items(self):
        while self.scene.selectedItems():
            item = self.scene.selectedItems()[0]
            if item.is_action():
                conn_to_delete = []
                for conn in self.connections:
                    for port in item.ports():
                        if conn.is_connected(port) and conn not in conn_to_delete:
                            conn_to_delete.append(conn)

                for conn in conn_to_delete:
                    try:
                        self.delete_connection(conn)
                    except:
                        print("Tried to delete connection again... probably...")

                self.delete_action(item)
            else:
                self.delete_connection(item)

    def delete_action(self, action):
        self.actions.remove(action)
        self.scene.removeItem(action)

    def delete_connection(self, conn):
        conn.port1.connections.remove(conn)
        conn.port2.connections.remove(conn)
        self.connections.remove(conn)
        self.scene.removeItem(conn)




