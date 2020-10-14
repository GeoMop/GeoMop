from PyQt5 import QtGui
from bgem.external import undo

from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files import format_last


class RegionItem(IdObject):
    _cols = ["cyan", "magenta", "darkRed", "darkCyan", "darkMagenta",
             "darkBlue", "yellow","blue"]
    # red and green is used for cut tool resp. cloud pixmap
    colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 1

    def __init__(self, id_map, color=None, name="", dim=-1, step=0.0, not_used=False, boundary=False, brep_shape_ids=[]):
        super(RegionItem, self).__init__()
        id_map.add(self)
        if color is None:
            color = RegionItem.colors[self.id % len(RegionItem.colors)].name()
        self.color = color

        self.name = name
        """Region name"""
        self.dim = dim
        """dimension (point = 0, well = 1, fracture = 2, bulk = 3)"""
        self.boundary = boundary
        """Is boundary region"""
        self.not_used = not_used
        self.mesh_step = float(step)
        self.brep_shape_ids = []
        """List of shape indexes - in BREP geometry """

        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    def save(self):
        return format_last.Region({ "color": self.color,
                                    "name": self.name,
                                    "dim": self.dim,
                                    "mesh_step": self.mesh_step,
                                    "boundary": self.boundary,
                                    "not_used": self.not_used,
                                    "brep_shape_ids": self.brep_shape_ids})

    @undo.undoable
    def set_name(self, name: str):
        old_name = self.name
        self.name = name
        yield "Set name"
        self.name = old_name

    @undo.undoable
    def set_color(self, color_name: str):
        old_color = self.color
        self.color = color_name
        yield "Set Color"
        self.color = old_color

    @undo.undoable
    def set_boundary(self, boundary: bool):
        self.boundary = boundary
        yield "Change region to/from boudary"
        self.boundary = not boundary

    @undo.undoable
    def set_region_mesh_step(self, mesh_step):
        old_step = self.mesh_step
        self.mesh_step = mesh_step
        yield "Set mesh step"
        self.mesh_step = old_step

    @undo.undoable
    def set_not_used(self, not_used: bool):
        self.not_used = not_used
        yield "Change region to/from used"
        self.not_used = not not_used