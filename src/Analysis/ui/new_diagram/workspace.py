"""
Workspace where all user input is processed.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""

from PyQt5 import QtWidgets, QtCore, QtGui, QtOpenGL
from .action import Action
from .connection import Connection


class Workspace(QtWidgets.QGraphicsView):
    """Graphics scene which handles user input and shows user the results."""
    def __init__(self, parent=None):
        """Initializes class."""
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
        self.setSceneRect(QtCore.QRectF(QtCore.QPoint(0, 0), QtCore.QPoint(10000000, 10000000)))

        # settings for zooming the workspace
        self.zoom = 1.0
        self.max_zoom = 5.0
        self.min_zoom = 0.3
        self.zoom_factor = 1.2

    @staticmethod
    def is_action(obj):
        """Return True if given object obj is an action."""
        if issubclass(type(obj), Action):
            return True
        else:
            return False

    def wheelEvent(self, event):
        """Handle zoom on wheel rotation."""
        degrees = event.angleDelta() / 8
        steps = degrees.y() / 15
        if steps > 0:
            self.zoom = min(self.max_zoom, self.zoom * self.zoom_factor)

        else:
            self.zoom = max(self.min_zoom, self.zoom / self.zoom_factor)

        self.setTransformationAnchor(self.AnchorUnderMouse)
        self.setTransform(QtGui.QTransform().scale(self.zoom, self.zoom))

    def contextMenuEvent(self, event):
        """Open context menu on right mouse button click."""
        self.new_action_pos = self.mapToScene(event.pos())
        self.edit_menu.exec_(event.globalPos())

    def add_action(self):
        """Create new action and add it to workspace."""
        self.actions.append(Action(None, self.new_action_pos))
        self.scene.addItem(self.actions[-1])

    def add_connection(self, port):
        """Create new connection from/to specified port and add it to workspace."""
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
        """If new connection is being crated, move the loose end to mouse position."""
        super(Workspace, self).mouseMoveEvent(event)
        if self.new_connection is not None:
            self.new_connection.set_port2_pos(self.mapToScene(event.pos()))

    def delete_items(self):
        """Delete all selected items from workspace."""
        while self.scene.selectedItems():
            """
            item = self.scene.selectedItems()[0]
            if self.is_action(item):
                for port in item.ports():
                    for conn in port.connections:
                        self.delete_connection(conn)
            """
            item = self.scene.selectedItems()[0]
            if self.is_action(item):
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
        """Delete specified action from workspace."""
        self.actions.remove(action)
        self.scene.removeItem(action)

    def delete_connection(self, conn):
        conn.port1.connections.remove(conn)
        conn.port2.connections.remove(conn)
        self.connections.remove(conn)
        self.scene.removeItem(conn)




