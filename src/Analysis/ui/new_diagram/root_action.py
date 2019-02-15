from PyQt5 import QtWidgets, QtCore, QtGui


class RootAction(QtWidgets.QGraphicsItem):
    def __init__(self):
        super(RootAction, self).__init__()

    def boundingRect(self):
        return self.childrenBoundingRect()

    def paint(self, painter, style, widget=None):
        pass

