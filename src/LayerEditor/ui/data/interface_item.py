from gm_base.geometry_files.format_last import Interface


class InterfaceItem:
    def __init__(self, elevation, transform_z=None, surface=None):
        super(InterfaceItem, self).__init__()
        self.surface = surface
        """Surface index"""
        self.transform_z = transform_z or [1.0, elevation]
        """Transformation in Z direction (scale and shift)."""
        self.elevation = elevation
        """ Representative Z coord of the surface."""

        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    def save(self):
        return Interface(dict(surface_id=self.surface.index if self.surface is not None else None,
                              transform_z=self.transform_z,
                              elevation=self.elevation))