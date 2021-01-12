from LayerEditor.ui.tools import undo
from gm_base.geometry_files.format_last import Interface


class InterfaceItem:
    def __init__(self, transform_z=None, surface=None, elevation=None):
        super(InterfaceItem, self).__init__()
        if transform_z is not None and elevation is not None and elevation != transform_z[1]:
            print("Elevation inconsistency! Elevation doesn't match transform_z! Choosing elevation as correct value.")
            transform_z[1] = elevation

        self.surface = surface
        """Surface index"""
        self.transform_z = transform_z or [1.0, elevation]
        """Transformation in Z direction (scale and shift)."""

        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    @property
    def elevation(self):
        """ Representative Z coord of the surface."""
        return self.transform_z[1]

    def save(self):
        return Interface(dict(surface_id=self.surface.index if self.surface is not None else None,
                              transform_z=self.transform_z,
                              elevation=self.elevation))

    @undo.undoable
    def set_elevation(self, new_elevation):
        old_elevation = self.elevation
        self.elevation = new_elevation
        yield "Changed Elevation"
        self.elevation = old_elevation


