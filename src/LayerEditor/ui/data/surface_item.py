import time

import numpy as np
import os

from bgem.bspline.bspline import Z_Surface

from LayerEditor.ui.tools import undo
from gm_base.geometry_files import format_last
from gm_base.geometry_files import bspline_io
import bgem.bspline.bspline_approx as ba


class SurfaceItem(format_last.Surface):
    """
    All data operations are performed here.
    TODO: distinguish changes that can be applied faster:
        - name - no need to recompute
        - xy_transform - just transformation of existing approximation
        - nuv, regularizace - recompute approx
    """
    def __init__(self, surf_data: format_last.Surface = None, _parent=None, copied_from=None):
        """ If surf_data is supplied copy it otherwise use default values from format_last.Surface
        :param surf: layer_structures.Surface
        """
        ### Common with GL Surface
        super().__init__()
        self._parent = _parent
        # Original quad
        self._quad = None
        # Elevation of the approximation.
        self._elevation = None
        # Approx object.
        self._approx_maker = None
        #
        self._changed_forms = False
        # Index of original surface. None for unsaved surface. Only used if this object is copy for SurfacePanel.
        self.copied_from = copied_from

        if surf_data is not None:
            self.grid_file = surf_data.grid_file
            """File with approximated points (grid of 3D points). None for plane"""
            self.file_skip_lines = surf_data.file_skip_lines
            """Number of header lines to skip. """
            self.file_delimiter = surf_data.file_delimiter
            """ Delimiter of data fields on a single line."""
            self.name = surf_data.name
            """Surface name"""
            start = time.time()
            if isinstance(surf_data.approximation, Z_Surface):
                approx = bspline_io.bs_zsurface_write(surf_data.approximation)
                self.approximation = bspline_io.bs_zsurface_read(approx)
            else:
                self.approximation = bspline_io.bs_zsurface_read(surf_data.approximation)
            self.update_from_z_surf()
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

    def get_index_from_list(self, lst: list):
        """Returns index of this object in provided list. If this object isn't in `lst` then return -1"""
        try:
            return lst.index(self)
        except ValueError:
            return -1

    def get_copied_from_index(self, lst: list):
        if self.copied_from is None:
            return -1
        else:
            return self.copied_from.get_index_from_list(lst)

    def update_from_surface(self, surf):
        """"""
        copied_from = self.copied_from
        for key, val in surf.__dict__.items():
            self.__dict__[key] = val
        self.copied_from = copied_from
        try:
            self._approx_maker = ba.SurfaceApprox.approx_from_file(self.grid_file, self.file_delimiter, self.file_skip_lines)
        except:
            return None
        return self

    def init_from_file(self, file):
        self._approx_maker = ba.SurfaceApprox.approx_from_file(file, self.file_delimiter,
                                                               self.file_skip_lines)
        self.grid_file = file
        self._quad = self._approx_maker.compute_default_quad()
        self._changed_forms = True
        return self

    def update_from_z_surf(self):
        self._quad = self.approximation.orig_quad
        self._elevation = self.approximation.center()[2]

    def set_name(self, name=None):
        self.name = name
        self._changed_forms = True

    def set_name_from_file(self, le_model):
        init_name = os.path.basename(self.grid_file)
        init_name, _ext = os.path.splitext(init_name)
        self.name = le_model.get_default_layer_name(init_name)

    def set_nuv(self, nuv):
        self.nuv = nuv
        self._changed_forms = True

    def set_xy_transform(self, xy_transform):
        self.xy_transform = xy_transform.tolist()
        self._changed_forms = True

    def get_actual_quad(self):
        if self._quad is None:
            return None
        quad_center = np.average(self._quad, axis=0)
        xy_mat = np.array(self.xy_transform, dtype = float)
        return np.dot((self._quad - quad_center), xy_mat[0:2, 0:2].T) + quad_center + xy_mat[0:2, 2]

    def compute_approximation(self):
        self.approximation = self._approx_maker.compute_adaptive_approximation(quad=self._quad,
                                                                               nuv=self.nuv,
                                                                               adapt_type="std_dev",
                                                                               std_dev=self.tolerance)
        self.update_from_z_surf()
        self.approx_error = self._approx_maker.error
        self._changed_forms = True

    def save_to_le_model(self, le_model):
        assert self.name != ""
        assert self.grid_file != ""
        assert self.approximation is not None
        if self.copied_from is None:
            # New surface.
            new_surface = SurfaceItem(self)
            le_model.add_surface(new_surface)
            self.copied_from = new_surface
        else:
            # Modify existing
            self.copied_from.update_from_surface(self)
        self._changed_forms = False

    def save(self, base_dir=None):
        return format_last.Surface(dict(grid_file=self.grid_file,
                                        file_skip_lines=self.file_skip_lines,
                                        file_delimiter=self.file_delimiter,
                                        name=self.name,
                                        approximation=bspline_io.bs_zsurface_write(self.approximation),
                                        approx_error=self.approx_error,
                                        tolerance=self.tolerance,
                                        xy_transform=self.xy_transform,
                                        nuv=self.nuv))
