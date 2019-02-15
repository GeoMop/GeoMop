"""
Workspace where all user input is processed.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import cProfile
import time
import random
from PyQt5 import QtWidgets, QtCore, QtGui, QtOpenGL
from .action import Action
from .connection import Connection
from .action_for_subactions import ActionForSubactions
from .root_action import RootAction


class Workspace(QtWidgets.QGraphicsView):
    """Graphics scene which handles user input and shows user the results."""
    def __init__(self, parent=None):
        """Initializes class."""
        super(Workspace, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.last_mouse_event_pos = QtCore.QPoint()
        self.viewport_moved = False

        self.edit_menu = self.parent().edit_menu
        self.edit_menu.new_action.triggered.connect(self.add_action)
        self.edit_menu.delete.triggered.connect(self.delete_items)
        self.edit_menu.add_random.triggered.connect(self.add_random_items)
        self.edit_menu.add_while.triggered.connect(self.add_while_loop)
        self.new_action_pos = QtCore.QPoint()
        self.setMouseTracking(True)
        self.actions_for_subactions = []
        self.actions = []
        self.connections = []
        self.new_connection = None
        self.setDragMode(self.RubberBandDrag)
        self.setSceneRect(QtCore.QRectF(QtCore.QPoint(-10000000, -10000000), QtCore.QPoint(10000000, 10000000)))
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(self.BoundingRectViewportUpdate)

        # settings for zooming the workspace
        self.zoom = 1.0
        self.zoom_factor = 1.1
        self.max_zoom = pow(self.zoom_factor, 10)
        self.min_zoom = pow(1/self.zoom_factor, 20)

        timer = QtCore.QTimer(self)
        #timer.timeout.connect(self.show_fps)
        timer.start(1000)
        self.fps_count = 0
        self.frame_time = 0

        self.prof = cProfile.Profile()
        self.prof.enable()

        self.root_item = RootAction()
        self.scene.addItem(self.root_item)


    @staticmethod
    def is_action(obj):
        """Return True if given object obj is an action."""
        if issubclass(type(obj), Action):
            return True
        else:
            return False

    def mousePressEvent(self, press_event):
        super(Workspace, self).mousePressEvent(press_event)
        self.last_mouse_event_pos = press_event.pos()

    def mouseMoveEvent(self, move_event):
        """If new connection is being crated, move the loose end to mouse position."""
        super(Workspace, self).mouseMoveEvent(move_event)
        if self.new_connection is not None:
            self.new_connection.set_port2_pos(self.mapToScene(move_event.pos()))
        if move_event.buttons() & QtCore.Qt.RightButton:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.viewport_moved = True
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() -
                                                (move_event.x() - self.last_mouse_event_pos.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() -
                                                (move_event.y() - self.last_mouse_event_pos.y()))

        self.last_mouse_event_pos = move_event.pos()

    def mouseReleaseEvent(self, release_event):
        super(Workspace, self).mouseReleaseEvent(release_event)
        '''
        self.last_mouse_event_pos = release_event.pos()
        mouse_grabber = self.scene.mouseGrabberItem()
        if mouse_grabber is not None and issubclass(type(mouse_grabber), Action):
            for item in self.items(release_event.pos()):
                if issubclass(type(item), ActionForSubactions) and item is not mouse_grabber:
                    mouse_grabber.setParentItem(item)
        '''

    def contextMenuEvent(self, event):
        """Open context menu on right mouse button click."""
        if not self.viewport_moved:
            self.new_action_pos = self.mapToScene(event.pos())
            self.edit_menu.exec_(event.globalPos())
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.viewport_moved = False

    def add_while_loop(self):
        self.actions.append(ActionForSubactions(None, self.new_action_pos))
        self.scene.addItem(self.actions[-1])

    def add_random_items(self):
        if not self.actions:
            self.new_action_pos = QtCore.QPoint(0, 0)
            self.add_action()
        for i in range(200):
            if i > 100:
                action = self.actions[random.randint(0,len(self.actions) - 1)]
                self.add_connection(action.ports()[random.randint(0, len(action.ports()) - 1)])
                action = self.actions[random.randint(0, len(self.actions) - 1)]
                self.add_connection(action.ports()[random.randint(0, len(action.ports()) - 1)])
            else:
                action = self.actions[random.randint(0, len(self.actions) - 1)]
                self.new_action_pos = action.pos() + QtCore.QPoint(random.randint(-800, 800), random.randint(-800, 800))
                self.add_action()

    def show_fps(self):
        print("Fps: " + str(self.fps_count))
        print("Avarage frame time: " + str(self.frame_time / (self.fps_count if self.fps_count else 1)))
        self.frame_time = 0
        self.fps_count = 0

        self.prof.disable()
        self.prof.print_stats()
        self.prof.clear()

        self.prof = cProfile.Profile()
        self.prof.enable()

    def wheelEvent(self, event):
        """Handle zoom on wheel rotation."""
        degrees = event.angleDelta() / 8
        steps = degrees.y() / 15
        self.setTransformationAnchor(self.AnchorUnderMouse)
        if steps > 0:
            if self.zoom < self.max_zoom:
                self.scale(self.zoom_factor, self.zoom_factor)
                self.zoom = self.zoom * self.zoom_factor
        else:
            if self.zoom > self.min_zoom:
                self.scale(1 / self.zoom_factor, 1 / self.zoom_factor)
                self.zoom = self.zoom / self.zoom_factor

    def paintEvent(self, event):
        start = time.time()

        super(Workspace, self).paintEvent(event)
        self.frame_time += time.time() - start
        self.fps_count += 1

    def add_action(self):
        """Create new action and add it to workspace."""
        self.actions.append(Action(self.root_item, self.new_action_pos))

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




