"""
Workspace where all user input is processed.
@author: Tomáš Blažek
@contact: tomas.blazek@tul.cz
"""
import cProfile
import time
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QFileDialog, QApplication

from .scene import Scene


class Workspace(QtWidgets.QGraphicsView):
    """Graphics scene which handles user input and shows user the results."""
    def __init__(self, workflow, edit_menu, parent=None):
        """Initializes class."""
        super(Workspace, self).__init__(parent)
        self.workflow = workflow
        self.scene = Scene(workflow, self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing, True)

        # for deciding if context menu should appear
        self.viewport_moved = False

        self.edit_menu = edit_menu

        self.setAcceptDrops(True)

        self.setDragMode(self.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(self.FullViewportUpdate)

        # settings for zooming the workspace
        self.zoom = 1.0
        self.zoom_factor = 1.1
        self.max_zoom = pow(self.zoom_factor, 10)
        self.min_zoom = pow(1/self.zoom_factor, 20)

        # timer for updating scene
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.scene.update_scene)
        timer.start(16.6)
        self.fps_count = 0
        self.frame_time = 0

        self.prof = cProfile.Profile()
        self.prof.enable()

        self.last_mouse_event_pos = QPoint(0, 0)
        self.mouse_press_event_pos = QPoint(0, 0)

    def _on_wf_changed(self):
        self.scene = Scene(self.module_view.current_workspace, self)
        self.setScene(self.scene)

    def mousePressEvent(self, press_event):
        """Store information about position where this event occurred."""
        super(Workspace, self).mousePressEvent(press_event)
        self.last_mouse_event_pos = press_event.pos()
        self.mouse_press_event_pos = press_event.pos()

    def dragEnterEvent(self, drag_enter):
        """Accept drag event if it carries action."""
        if drag_enter.mimeData().hasText():
            if drag_enter.mimeData().text() in ["_ActionBase", "List"]:
                drag_enter.acceptProposedAction()

    def dropEvent(self, drop_event):
        """Create new action from dropped information"""
        self.scene.new_action_pos = self.mapToScene(drop_event.pos()) - drop_event.source().get_pos_correction()
        self.scene.add_action(self.mapToScene(drop_event.pos()) - drop_event.source().get_pos_correction(),
                              drop_event.mimeData().text())
        drop_event.acceptProposedAction()

    def dragMoveEvent(self, move_event):
        move_event.acceptProposedAction()

    def mouseMoveEvent(self, move_event):
        """ If new connection is being crated, move the loose end to mouse position.
            If user drags with right button pressed, move visible rectangle. """
        super(Workspace, self).mouseMoveEvent(move_event)
        if self.scene.new_connection is not None:
            self.scene.new_connection.set_port2_pos(self.mapToScene(move_event.pos()))
            self.scene.update()

        dist = (self.mouse_press_event_pos - move_event.pos()).manhattanLength()
        if move_event.buttons() & QtCore.Qt.RightButton and dist >= QApplication.startDragDistance():
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
        """Open context menu on right mouse button click if no dragging occurred."""
        super(Workspace, self).contextMenuEvent(event)
        if not self.viewport_moved:
            self.scene.new_action_pos = self.mapToScene(event.pos())
            self.edit_menu.exec_(event.globalPos())
        else:
            self.setCursor(QtCore.Qt.ArrowCursor)
            self.viewport_moved = False

    def show_fps(self):
        """Debug tool"""
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
        if self.center_on_content:
            self.center_on_content = False
            self.centerOn(self.scene.itemsBoundingRect().center())
        start = time.time()

        super(Workspace, self).paintEvent(event)
        self.frame_time += time.time() - start
        self.fps_count += 1

    def save(self):
        save_location = QFileDialog.getSaveFileName(self.parent(), "Select Save Location")
        print(save_location)
        with open(save_location[0],'w') as save_file:
            self.scene.save_item(save_file, self.scene.action_model.get_item())

    def load(self):
        pass
