from PyQt5 import QtGui

from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files import format_last


class Region(IdObject):
    _cols = ["cyan", "magenta", "darkRed", "darkCyan", "darkMagenta",
             "darkBlue", "yellow","blue"]
    # red and green is used for cut tool resp. cloud pixmap
    colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 1

    def __init__(self, color=None, name="", dim=-1, step=0.0, boundary=False):
        super(Region, self).__init__()

        if color is None:
            color = Region.colors[self.id % len(Region.colors)].name()
        self.color = color

        self.name = name
        """Region name"""
        self.dim = dim
        """dimension (point = 0, well = 1, fracture = 2, bulk = 3)"""
        self.boundary = boundary
        """Is boundary region"""
        self.mesh_step = float(step)

    @staticmethod
    def make_from_data(region_data:format_last.Region):
        return Region(region_data.color,
                      region_data.name,
                      region_data.dim,
                      region_data.mesh_step,
                      region_data.boundary)

    def convert_to_data(region_data: format_last.Region):
        return format_last.Region({ "color": region_data.color,
                                    "name": region_data.name,
                                    "dim": region_data.dim,
                                    "mesh_step": region_data.mesh_step,
                                    "boundary": region_data.boundary})
