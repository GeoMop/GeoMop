from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QLinearGradient

from .gport import GPort


class GWorkflowInputPort(GPort):
    def __init__(self, index=0, pos=QPoint(0,0), name="", parent=None):
        super(GWorkflowInputPort, self).__init__(index, pos, name, parent)
        self.setPath(self.draw_port_path())
        gradient = QLinearGradient(QPoint(GPort.RADIUS, -6 * GPort.RADIUS), QPoint(GPort.RADIUS, GPort.RADIUS))
        gradient.setColorAt(1.0, QtCore.Qt.black)
        gradient.setColorAt(0.0, QtCore.Qt.transparent)
        self.line_pen = QtGui.QPen(gradient, 2, QtCore.Qt.DashLine)
        self.port_pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.DashLine)
        self.setPen(self.port_pen)
        self.setEnabled(False)

    def setEnabled(self, bool):
        super(GPort, self).setEnabled(bool)

    def draw_port_path(self):
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addEllipse(QtCore.QRectF(0, 0, self.RADIUS * 2, self.RADIUS * 2))

        p.moveTo(QPoint(GPort.RADIUS, -6 * GPort.RADIUS))
        p.lineTo(QPoint(GPort.RADIUS, GPort.RADIUS))
        return p

    def paint(self, painter, style, widget=None):
        super(GWorkflowInputPort, self).paint(painter, style, widget)


