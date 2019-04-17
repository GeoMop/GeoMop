from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QPoint


class RootAction(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(RootAction, self).__init__()
        self.setPos(QPoint(0,0))

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, style, widget=None):
        pass

