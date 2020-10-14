from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import Surface


class SurfaceItem():
    def __init__(self, surf_data: Surface):
        self.grid_file = surf_data.grid_file
        """File with approximated points (grid of 3D points). None for plane"""
        self.file_skip_lines = surf_data.file_skip_lines
        """Number of header lines to skip. """
        self.file_delimiter = surf_data.file_skip_lines
        """ Delimiter of data fields on a single line."""
        self.name = surf_data.name
        """Surface name"""
        self.approximation = surf_data.approximation
        """Serialization of the  Z_Surface."""
        self.regularization = surf_data.regularization
        """Regularization weight."""
        self.approx_error = surf_data.approx_error
        """L-inf error of aproximation"""

        self.index = None
        """Reserved for referencing by index while saving. Should be cleared back to None after saving is finished"""

    def save(self):
        return Surface(dict(grid_file=self.grid_file,
                            file_skip_lines=self.file_skip_lines,
                            file_delimiter=self.file_delimiter,
                            name=self.name,
                            approximation=self.approximation,
                            regularization=self.regularization,
                            approx_error=self.approx_error))