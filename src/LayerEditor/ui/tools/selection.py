from PyQt5.QtCore import pyqtSignal, QObject

from LayerEditor.ui.data.region_item import RegionItem


class Selection(QObject):
    selection_changed = pyqtSignal()
    """Selection has changed"""
    def __init__(self):
        super(Selection, self).__init__()
        self._diagram = None
        self._selected = []

    def set_diagram(self, diagram):
        self._diagram = diagram

    def select_item(self, item):
        self._selected.clear()
        self.select_toggle_item(item)
        self._diagram.update()

        self.selection_changed.emit()

    def select_toggle_item(self, item):
        if item in self._selected:
            self._selected.remove(item)
        else:
            self._selected.append(item)
        self._diagram.update()

        self.selection_changed.emit()

    def select_all(self):
        self._selected.clear()
        self._selected.extend(self._diagram.points.values())
        self._selected.extend(self._diagram.segments.values())
        self._selected.extend(self._diagram.polygons.values())
        self._diagram.update()

        self.selection_changed.emit()

    def deselect_all(self, emit=True):
        self._selected.clear()
        self._diagram.update()

        if emit:
            self.selection_changed.emit()

    def is_selected(self, item):
        return item in self._selected

    def max_selected_dim(self):
        if self._selected:
            return max([ g_item.dim for g_item in self._selected])
        else:
            return 0

    def deselect_item_if_exists(self, g_item):
        if g_item in self._selected:
            self._selected.remove(g_item)

    def get_selected_shape_dim_id(self):
        r = []
        for g_item in self._selected:
            r.append((g_item.dim, g_item.shape_id))
        return r
