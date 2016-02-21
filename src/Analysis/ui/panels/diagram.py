"""CanvasWidget file"""

import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

class Diagram(QtWidgets.QGraphicsScene):
    """GeoMop design area"""

    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Diagram, self).__init__(parent)
        self._pictures = None

    def mouseMoveEvent(self, mouseEvent):
        # editor.sceneMouseMoveEvent(mouseEvent)
        super(Diagram, self).mouseMoveEvent(mouseEvent)
        
    def mouseReleaseEvent(self, mouseEvent):
        # editor.sceneMouseReleaseEvent(mouseEvent)
        super(Diagram
        , self).mouseReleaseEvent(mouseEvent)
