from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, QPoint, QPointF
from PyQt5.QtGui import QPolygonF

from LayerEditor.ui.diagram_editor.diagram_scene import DiagramScene


class DiagramView(QtWidgets.QGraphicsView):
    cursorChanged = pyqtSignal(float, float)
    def __init__(self, le_model):
        super(DiagramView, self).__init__()
        self.scenes = {}  # {topology_id: DiagramScene}
        # dict of all scenes
        self._empty = True

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        self.el_map = {}

        for block in le_model.blocks.values():
            diagram_scene = DiagramScene(block, le_model.init_area.boundingRect(), self)

            block.selection.set_diagram(diagram_scene)
            self.scenes[block.id] = diagram_scene

        self.setScene(self.scenes[0])
        """scene is set here only temporarily until there will be Layer Panel"""

        scale = le_model.init_zoom_pos_data["zoom"]
        self.scale(scale, scale)
        self.centerOn(QPointF(le_model.init_zoom_pos_data["x"],
                              -le_model.init_zoom_pos_data["y"]))

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            scale = 1.25
        else:
            scale = 0.8
        self.scale(scale, scale)
        self.scene().update_zoom(self.zoom)

    @property
    def zoom(self):
        return self.transform().m11()

    """
    def show_map(self):
        file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "res", "bukov_situace.svg")
        map = QtSvg.QGraphicsSvgItem(file)

        # map transform
        # 622380 - 247.266276267186
        # 1128900 - 972.212997362655
        # 1128980 - 1309.97292588439
        map.setTransformOriginPoint(247.266276267186, 972.212997362655)
        map.setScale((1128980 - 1128900) / (1309.97292588439 - 972.212997362655))
        map.setPos(-622380 - 247.266276267186, 1128900 - 972.212997362655)

        self._scene.addItem(map)
        map.setCursor(QtCore.Qt.CrossCursor)
    """

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        super(DiagramView, self).mouseMoveEvent(event)
        pos = self.mapToScene(event.pos())
        self.cursorChanged.emit(pos.x(), pos.y())

    def setScene(self, scene: DiagramScene) -> None:
        super(DiagramView, self).setScene(scene)
        self.scene().update_zoom(self.zoom)
        scene.update_scene()

    def save(self):
        center = self.mapToScene(self.viewport().rect().center())

        return {"init_area": [(point.x(), point.y()) for point in QPolygonF(self.sceneRect())][:-1],
                "zoom": {"zoom": self.zoom,
                         "x": center.x(),
                         "y": -center.y(),
                         'position_set': False}}