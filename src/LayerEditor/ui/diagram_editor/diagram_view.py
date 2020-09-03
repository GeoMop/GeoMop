from PyQt5 import QtGui, QtWidgets, QtCore


class DiagramView(QtWidgets.QGraphicsView):
    def __init__(self):

        super(DiagramView, self).__init__()

        self._zoom = 1
        self._empty = True
        self.scenes = []

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        self.el_map = {}

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._zoom *= 1.25
        else:
            self._zoom *= 0.8
        self.scale(self._zoom, self._zoom)

        self.scene().update_zoom(self.transform().m11())

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
