"""
Workspace where all user input is processed.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import cProfile
import time
from PyQt5 import QtWidgets, QtCore, QtGui, QtOpenGL
from .action import Action
from .connection import Connection
from .action_for_subactions import ActionForSubactions
from .scene import Scene


class Workspace(QtWidgets.QGraphicsView):
    """Graphics scene which handles user input and shows user the results."""
    def __init__(self, parent=None):
        """Initializes class."""
        super(Workspace, self).__init__(parent)
        self.scene = Scene()
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)
        self.last_mouse_event_pos = QtCore.QPoint()
        self.viewport_moved = False

        self.edit_menu = self.parent().edit_menu
        self.edit_menu.new_action.triggered.connect(self.scene.add_action)
        self.edit_menu.delete.triggered.connect(self.scene.delete_items)
        self.edit_menu.add_random.triggered.connect(self.scene.add_random_items)
        self.edit_menu.order.triggered.connect(self.scene.order_diagram)
        #self.edit_menu.add_while.triggered.connect(self.scene.add_while_loop)

        #self.setMouseTracking(True)

        self.setDragMode(self.RubberBandDrag)
        self.setSceneRect(QtCore.QRectF(QtCore.QPoint(-10000000, -10000000), QtCore.QPoint(10000000, 10000000)))
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(self.MinimalViewportUpdate)

        # settings for zooming the workspace
        self.zoom = 1.0
        self.zoom_factor = 1.1
        self.max_zoom = pow(self.zoom_factor, 10)
        self.min_zoom = pow(1/self.zoom_factor, 20)

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.scene.update_scene)
        timer.start(16.6)
        self.fps_count = 0
        self.frame_time = 0

        self.prof = cProfile.Profile()
        self.prof.enable()

    def mousePressEvent(self, press_event):
        super(Workspace, self).mousePressEvent(press_event)
        self.last_mouse_event_pos = press_event.pos()

    def mouseMoveEvent(self, move_event):
        """If new connection is being crated, move the loose end to mouse position."""
        super(Workspace, self).mouseMoveEvent(move_event)
        if self.scene.new_connection is not None:
            self.scene.new_connection.set_port2_pos(self.mapToScene(move_event.pos()))
            self.scene.update()
        if move_event.buttons() & QtCore.Qt.RightButton:
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            self.viewport_moved = True
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() -
                                                (move_event.x() - self.last_mouse_event_pos.x()))
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() -
                                                (move_event.y() - self.last_mouse_event_pos.y()))
            self.scene.update()
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
        super(Workspace, self).contextMenuEvent(event)
        if not self.viewport_moved:
            self.scene.new_action_pos = self.mapToScene(event.pos())
            self.edit_menu.exec_(event.globalPos())
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.viewport_moved = False

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

