from PyQt5 import QtGui, QtCore


class Cursor:
    @classmethod
    def setup_cursors(cls):
        cls.point = QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        cls.segment = QtGui.QCursor(QtCore.Qt.UpArrowCursor)
        cls.polygon = QtGui.QCursor(QtCore.Qt.CrossCursor)
        cls.draw = QtGui.QCursor(QtCore.Qt.ArrowCursor)

class Selection():
    def __init__(self, diagram):
        self._diagram = diagram
        self._selected = []

    def select_item(self, item):
        self._selected.clear()
        self.select_add_item(item)
        self._diagram.update()

        self._diagram.selection_changed.emit()

    def select_add_item(self, item):
        if item in self._selected:
            self._selected.remove(item)
        else:
            self._selected.append(item)
        self._diagram.update()

        self._diagram.selection_changed.emit()

    def select_all(self):
        self._selected.clear()
        self._selected.extend(self._diagram.points.values())
        self._selected.extend(self._diagram.segments.values())
        self._selected.extend(self._diagram.polygons.values())
        self._diagram.update()

        self._diagram.selection_changed.emit()

    def deselect_all(self, emit=True):
        self._selected.clear()
        self._diagram.update()

        if emit:
            self._diagram.selection_changed.emit()

    def is_selected(self, item):
        return item in self._selected