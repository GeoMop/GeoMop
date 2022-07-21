from PyQt5 import QtGui, QtCore


class Cursor:
    @classmethod
    def setup_cursors(cls):
        cls.point = QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        cls.segment = QtGui.QCursor(QtCore.Qt.UpArrowCursor)
        cls.polygon = QtGui.QCursor(QtCore.Qt.CrossCursor)
        cls.draw = QtGui.QCursor(QtCore.Qt.ArrowCursor)