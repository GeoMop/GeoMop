from PyQt5 import QtGui

from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files import format_last


class Region(IdObject):
    _cols = ["cyan", "magenta", "darkRed", "darkCyan", "darkMagenta",
             "darkBlue", "yellow","blue"]
    # red and green is used for cut tool resp. cloud pixmap
    colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 1

    def __init__(self, id_map, color=None, name="", dim=-1, step=0.0, not_used=False, boundary=False):
        super(Region, self).__init__()
        id_map.add(self)
        if color is None:
            color = Region.colors[self.id % len(Region.colors)].name()
        self.color = color

        self.name = name
        """Region name"""
        self.dim = dim
        """dimension (point = 0, well = 1, fracture = 2, bulk = 3)"""
        self.boundary = boundary
        """Is boundary region"""
        self.not_used = not_used
        self.mesh_step = float(step)

    def convert_to_data(self):
        return format_last.Region({ "color": self.color,
                                    "name": self.name,
                                    "dim": self.dim,
                                    "mesh_step": self.mesh_step,
                                    "boundary": self.boundary,
                                    "not_used": self.not_used})

    # TODO: Make undoable, maybe?
    def set_color(self, color_name: str):
        self.color = color_name

    # TODO: Make undoable, maybe?
    def set_boundary(self, boundary: bool):
        self.boundary = boundary

    # TODO: Make undoable, maybe?
    def set_region_mesh_step(self, mesh_step):
        self.mesh_step = mesh_step

    # TODO: Make undoable, maybe?
    def set_not_used(self, not_used: bool):
        self.not_used = not_used