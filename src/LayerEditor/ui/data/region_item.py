import random

from PyQt5 import QtGui
from PyQt5.QtGui import QColor
from LayerEditor.ui.tools import undo

from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files import format_last


class RegionItem(IdObject):
    _cols = ["gray", "white"]
    used_colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 1

    def __init__(self, region_data):
        super(RegionItem, self).__init__()
        if region_data.color == "":
            self.color = self.get_distinct_color().name()
        else:
            self.color = region_data.color
        RegionItem.used_colors.append(QtGui.QColor(self.color))

        self.name = region_data.name
        """Region name"""
        self.dim = region_data.dim
        """dimension (point = 0, well = 1, fracture = 2, bulk = 3)"""
        self.boundary = region_data.boundary
        """Is boundary region"""
        self.not_used = region_data.not_used
        self.mesh_step = float(region_data.mesh_step)
        self.brep_shape_ids = region_data.brep_shape_ids
        """List of shape indexes - in BREP geometry """

        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    def get_distinct_color(self, tries=40):
        last_dist = 0
        for y in range(tries):
            candidate = QColor(random.randint(0, 256), random.randint(0, 256), random.randint(0, 256))
            dists = []
            for color in RegionItem.used_colors:
                c1 = color
                c2 = candidate
                r = (c1.red() + c2.red()) / 2
                dist = (2 + r / 256) * (c1.red() - c2.red()) ** 2 + 4 * (c1.green() - c2.green()) ** 2 + (
                            2 + (255 - r) / 256) * (c1.blue() - c2.blue()) ** 2
                dists.append(dist)
            dist = min(dists)
            if dist > last_dist:
                winner = candidate
                last_dist = dist
        return winner

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