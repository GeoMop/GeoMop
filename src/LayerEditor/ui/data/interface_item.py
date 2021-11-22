from LayerEditor.ui.data.abstract_item import AbstractItem
from LayerEditor.ui.tools import undo
from gm_base.geometry_files.format_last import Interface


class InterfaceItem(AbstractItem):
    def __init__(self):
        AbstractItem.__init__(self)
        self.surface = None
        self.transform_z = (1.0, 0.0)

    def deserialize(self, transform_z, surface):
        """ Initializes interface with data from format_last.py
            :data: transform_z and surface"""
        self.surface = surface
        """Surface index"""
        self.transform_z = transform_z
        """Transformation in Z direction (scale and shift)."""

    @property
    def elevation(self):
        """ Representative Z coord of the surface."""
        return self.transform_z[1]

    @elevation.setter
    def elevation(self, new_elevation):
        """ Representative Z coord of the surface."""
        self.transform_z = (self.transform_z[0], new_elevation)

    def serialize(self):
        return Interface(dict(surface_id=self.surface.index if self.surface is not None else None,
                              transform_z=self.transform_z,
                              elevation=self.elevation))

    @undo.undoable
    def set_elevation(self, new_elevation):
        old_elevation = self.elevation
        self.transform_z = (self.transform_z[0], new_elevation)
        yield "Changed Elevation"
        self.transform_z = (self.transform_z[0], old_elevation)


