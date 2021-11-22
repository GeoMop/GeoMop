import time

import numpy as np
import os

from bgem.bspline.bspline import Z_Surface

from LayerEditor.ui.data.abstract_item import AbstractItem
from LayerEditor.ui.tools import undo
from gm_base.geometry_files import format_last
from gm_base.geometry_files import bspline_io
import bgem.bspline.bspline_approx as ba


class SurfaceItem(format_last.Surface, AbstractItem):
    """
    All data operations are performed here.
    TODO: distinguish changes that can be applied faster:
        - name - no need to recompute
        - xy_transform - just transformation of existing approximation
        - nuv, regularizace - recompute approx
    """
    def __init__(self):
        """ If surf_data is supplied copy it otherwise use default values from format_last.Surface
        :param surf: layer_structures.Surface
        """
        ### Common with GL Surface
        super().__init__()

    @property
    def overlay_name(self):
        return self.name

    def deserialize(self, surf_data: format_last.Surface):
        self.grid_file = surf_data.grid_file
        """File with approximated points (grid of 3D points). None for plane"""
        self.file_skip_lines = surf_data.file_skip_lines
        """Number of header lines to skip. """
        self.file_delimiter = surf_data.file_delimiter
        """ Delimiter of data fields on a single line."""
        self.name = surf_data.name
        """Surface name"""
        if isinstance(surf_data.approximation, Z_Surface):
            approx = bspline_io.bs_zsurface_write(surf_data.approximation)
            self.approximation = bspline_io.bs_zsurface_read(approx)
        else:
            self.approximation = bspline_io.bs_zsurface_read(surf_data.approximation)
        self._changed_forms = False
        """Serialization of the  Z_Surface."""
        self.tolerance = surf_data.tolerance
        """Regularization weight."""
        self.approx_error = surf_data.approx_error
        """L-inf error of aproximation"""
        self.xy_transform = surf_data.xy_transform
        """Transformation matrix np array 2x3, shift vector in last column."""
        self.nuv = surf_data.nuv
        """Approximation grid dimensions. (u,v)"""
        self._approx_maker = ba.SurfaceApprox.approx_from_file(self.grid_file,
                                                               self.file_delimiter,
                                                               self.file_skip_lines)

    @property
    def elevation(self):
        return self.approximation.center()[2]

    def get_index_from_list(self, lst: list):
        """Returns index of this object in provided list. If this object isn't in `lst` then return -1"""
        try:
            return lst.index(self)
        except ValueError:
            return -1

    def serialize(self):
        return format_last.Surface(dict(grid_file=self.grid_file,
                                        file_skip_lines=self.file_skip_lines,
                                        file_delimiter=self.file_delimiter,
                                        name=self.name,
                                        approximation=bspline_io.bs_zsurface_write(self.approximation),
                                        approx_error=self.approx_error,
                                        tolerance=self.tolerance,
                                        xy_transform=self.xy_transform,
                                        nuv=self.nuv))

    def get_curr_quad(self):
        """
        Return quad, u_knots, v_knots for grid plot in mainwindow._show_grid."""
        approx = self.approximation
        if approx is not None:
            ur = approx.u_basis.knots_idx_range
            u_knots = [approx.u_basis.knots[i] / approx.u_basis.domain_size
                       for i in range(ur[0] + 1, ur[1])]
            vr = approx.v_basis.knots_idx_range
            v_knots = [approx.v_basis.knots[i] / approx.v_basis.domain_size
                       for i in range(vr[0] + 1, vr[1])]
        else:
            u_knots = []
            v_knots = []
        quad = self.get_actual_quad()
        return quad, u_knots, v_knots

    def get_actual_quad(self):
        quad = self.approximation.quad
        if quad is None:
            return None
        quad_center = np.average(quad, axis=0)
        xy_mat = np.array(self.xy_transform, dtype = float)
        return np.dot((quad - quad_center), xy_mat[0:2, 0:2].T) + quad_center + xy_mat[0:2, 2]
