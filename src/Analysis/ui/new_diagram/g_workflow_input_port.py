from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QLinearGradient

from .gport import GPort


class GWorkflowInputPort(GPort):
    def __init__(self, index=0, pos=QPoint(0,0), name="", parent=None):
        super(GWorkflowInputPort, self).__init__(index, pos, name, parent)
        gradient = QLinearGradient(QPoint(GPort.RADIUS, -6 * GPort.RADIUS), QPoint(GPort.RADIUS, GPort.RADIUS))
        gradient.setColorAt(1.0, QtCore.Qt.black)
        gradient.setColorAt(0.0, QtCore.Qt.transparent)
        self.setPen(QtGui.QPen(gradient, 1.2, QtCore.Qt.DashLine))
        self.setEnabled(False)
        self.setPath(self.draw_port_path())

    def setEnabled(self, bool):
        super(GPort, self).setEnabled(bool)

    def draw_port_path(self):
        self.prepareGeometryChange()
        p = QtGui.QPainterPath()
        p.addEllipse(QtCore.QRectF(0, 0, self.RADIUS * 2, self.RADIUS * 2))

        p.moveTo(QPoint(GPort.RADIUS, -6 * GPort.RADIUS))
        p.lineTo(QPoint(GPort.RADIUS, GPort.RADIUS))
        return p


