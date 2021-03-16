import os

import numpy as np
import bgem.bspline.bspline_approx as ba

from LayerEditor.ui.data.surface_item import SurfaceItem
from gm_base.geometry_files import format_last, bspline_io


class SurfaceItemDraft(format_last.Surface):
    def __init__(self):
        super(SurfaceItemDraft, self).__init__()
        self._quad = None
        # Elevation of the approximation.
        self._elevation = None
        # Approx object.
        self._approx_maker = None
        #
        self._changed_forms = False
        # Index of original surface. None for unsaved surface. Only used if this object is copy for SurfacePanel.
        self.copied_from = None
        """Index of original surface. None for unsaved surface. Only used if this object is copy for SurfacePanel."""

    def copy_from_surface_item(self, surf_item):
        for key, val in surf_item.__dict__.items():
            self.__dict__[key] = val
        approx = bspline_io.bs_zsurface_write(surf_item.approximation)
        self.approximation = bspline_io.bs_zsurface_read(approx)
        self.copied_from = surf_item
        self.update_from_z_surf()
        self._changed_forms = False

    def get_copied_from_index(self, lst: list):
        if self.copied_from is None:
            return -1
        else:
            return self.copied_from.get_index_from_list(lst)

    def update_from_z_surf(self):
        self._quad = self.approximation.orig_quad
        self._elevation = self.approximation.center()[2]

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
            new_surface = SurfaceItem.create_from_data(self)
            le_model.add_surface(new_surface)
            self.copied_from = new_surface
        else:
            # Modify existing
            self.copied_from.deserialize(self)
            new_surface = None
        self._changed_forms = False

        return new_surface