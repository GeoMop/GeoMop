import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

import os
import numpy as np
import copy

import gm_base.b_spline
import bspline_approx as ba
from gm_base.geomop_dialogs import GMErrorDialog
import gm_base.icon as icon
import gm_base.geometry_files.format_last as GL

"""
TODO:
Why is approx error so large. Debug display error distribution.
"""


class SurfFormData(GL.Surface):
    """
    All data operations are performed here.
    TODO: distinguish changes that can be applied faster:
        - name - no need to recompute
        - xy_transform - just transformation of existing approximation
        - nuv, regularizace - recompute approx
    """
    def __init__(self):
        """
        :param surf: layer_structures.Surface
        """
        ### Common with GL Surface
        super().__init__()
        # self.name = ""
        # self.grid_file = ""
        # self.file_skip_lines = 0
        # self.file_delimiter = ' '
        # self.approximation = ClassFactory(SurfaceApproximation), # converted to ZSurface during IO
        # self.regularization = 1.0
        # self.approx_error = 0.0


        # Approximation grid dimensions. (u,v)
        self._nuv = None

        # Approximation reglularization parameter
        self.regularization = 1.0

        # Original quad
        self._quad = None

        # Transformation matrix np array 2x3, shift vector in last column.
        self._xy_transform = np.array([[1, 0, 0], [0, 1, 0]], dtype = float)

        # Elevation of the approximation.
        self._elevation = None

        # Approx object.
        self._approx_maker = None

        #
        self._changed_forms = False

        # Index of original surface. None for unsaved surface.
        self._idx = -1



    @classmethod
    def init_from_surface(cls, surf, idx):
        self = cls()
        for key, val in surf.__dict__.items():
            self.__dict__[key] = val
        self._idx = idx
        try:
            self._approx_maker = ba.SurfaceApprox.approx_from_file(self.grid_file, self.file_delimiter, self.file_skip_lines)
        except:
            return None

        return self

    def init_from_file(self):
        try:
            self._approx_maker = ba.SurfaceApprox.approx_from_file(self.grid_file, self.file_delimiter, self.file_skip_lines)
        except:
            return None
        self._quad = self._approx_maker.compute_default_quad()
        self._nuv = self._approx_maker.compute_default_nuv()
        self._changed_forms = True
        return self

    def update_from_z_surf(self):
        u = self.approximation.u_basis.n_intervals
        v = self.approximation.v_basis.n_intervals
        self._nuv = (u, v)
        self._quad = self.approximation.orig_quad
        self._xy_transform = self.approximation.get_transform()[0]
        self._elevation = self.approximation.center()[2]


    def set_name(self, name):
        self.name = name
        self._changed_forms = True

    def set_nuv(self, nuv):
        self._nuv = nuv
        self._changed_forms = True

    def set_xy_transform(self, xy_transform):
        self._xy_transform = xy_transform
        self._changed_forms = True

    def get_actual_quad(self):
        if self._quad is None:
            return None
        quad_center = np.average(self._quad, axis=0)
        xy_mat = self._xy_transform
        return np.dot((self._quad - quad_center), xy_mat[0:2, 0:2].T) + quad_center + xy_mat[0:2, 2]

    def compute_approximation(self):
        self.approximation = self._approx_maker.compute_approximation(
            quad = self.get_actual_quad(),
            nuv = self._nuv,
            regularization_weight = self.regularization)
        self.update_from_z_surf()
        self.approx_error = self._approx_maker.error
        self._changed_forms = True

    def save_to_layers(self, layers):
        assert self.name != ""
        assert self.grid_file != ""
        assert self.approximation is not None
        new_surface = copy.copy(self)
        if self._idx == -1:
            # New surface.
            layers.add_surface(new_surface)
            self._idx = len(layers.surfaces) - 1
        else:
            # Modify existing
            layers.set_surface(self._idx, new_surface)
        self._changed_forms = False


class SurfacesComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.setEnabled(False)

    def set_items(self, surfaces, new_idx = 0, name = ""):
        self.blockSignals(True)
        self.clear()
        for idx, surf in enumerate(surfaces):
            self.addItem( surf.name,  idx)
        if new_idx == -1:
            self.addItem(name, -1)
            new_idx = self.count() - 1
        self.setCurrentIndex(new_idx)
        self.blockSignals(False)

class WgShowButton(QtWidgets.QPushButton):
    """
    Toggle visibility button.
    signal: toggled
    use setChecked to set visibility
    use blockSignals to fix the state
    """
    def __init__(self, tooltip, parent):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.set_icon()

    def nextCheckState(self):
        visible = self.isChecked()
        self.setChecked(not visible)
        self.set_icon()

    def set_icon(self):
        visible = self.isChecked()
        if visible:
            self.setIcon(icon.get_app_icon("visible"))
        else:
            self.setIcon(icon.get_app_icon("hidden"))






"""TODO: must set a current surface, need handler in main class."""

class Surfaces(QtWidgets.QWidget):
    """
    GeoMop Layer editor surfaces panel
    
    pyqtSignals:
        * :py:attr:`show_grid

    All regions function contains history operation without label and
    must be placed after first history operation with label.
    """


    show_grid = QtCore.pyqtSignal(bool)
    """Signal is sent when mash shoud be show o repaint.    
    :param bool force: if force not set, don't call mash if already exist
    """


    def __init__(self, layers, home_dir, parent=None):
        """
        :param layers: Layers data object (i.e. parent data object where we may read and write the data)
        :param home_dir: Where to start Open file dialog.
                        TODO: introduce a sort of file management object, that can provide this info and save recent ...
        :param parent: Surface panel parent.
        """
        super().__init__(parent)

        # Data class for the surface panel.
        self.data = SurfFormData()
        # Surfaces list in Layers.
        self.layers = layers
        # Home dir (this way fixed through one LayerEditor session.)
        self.home_dir = home_dir

        # Setup child widgets
        grid = QtWidgets.QGridLayout(self)
        self.setLayout(grid)

        surf_row = QtWidgets.QHBoxLayout()

        wg_suface_lbl = QtWidgets.QLabel("Surface:")
        grid.addWidget(wg_suface_lbl, 0, 0, 1, 3)
        grid.addLayout(surf_row, 1, 0, 1, 3)

        self.wg_view_button = WgShowButton("Switch visibilty of the surface grid.", parent = self)
        self.wg_view_button.toggled.connect(self.show_grid)

        # surface cobobox
        self.wg_surf_combo = SurfacesComboBox()
        self.wg_surf_combo.currentTextChanged.connect(self.data.set_name)
        self.wg_surf_combo.currentIndexChanged.connect(self.change_surface)

        self.wg_add_button = self._make_button(
            "add", None, 'Add new surface to the assignable list.',
            self.add_surface_from_file)
        self.wg_rm_button = self._make_button(
            "remove", None, 'Remove selected surface from the list.',
            self.rm_surface)

        surf_row.addWidget(self.wg_view_button)
        surf_row.addWidget(self.wg_surf_combo, stretch = 10)
        surf_row.addWidget(self.wg_add_button)
        surf_row.addWidget(self.wg_rm_button)
        #grid.addWidget(self._make_separator(), 2, 0, 1, 3)
        
        # grid file
        file_row = QtWidgets.QHBoxLayout()
        grid.addLayout(file_row, 2, 0, 1, 3)
        self.wg_reload_button = self._make_button(
            "folder", None, 'Refresh the working surface.',
            self.reload)
        self.wg_file_le = self._make_read_only_line()

        file_row.addWidget(self.wg_reload_button)
        file_row.addWidget(self.wg_file_le, stretch=10)

        import_row = QtWidgets.QHBoxLayout()
        grid.addLayout(import_row, 3, 0, 1, 3)
        wg_header_lbl = QtWidgets.QLabel("Skip:")
        self.wg_skip_lines_le = self._make_skip_lines_le()

        # delimiter
        wg_delimiter_lbl = QtWidgets.QLabel("Delimiter:")
        self.wg_delimiter_cb = self._make_delimiter_combo()

        import_row.addWidget(wg_header_lbl)
        import_row.addWidget(self.wg_skip_lines_le)
        import_row.addWidget(wg_delimiter_lbl)
        import_row.addWidget(self.wg_delimiter_cb)
        grid.addWidget(self._make_separator(), 4, 0, 1, 3)

        # xz scale
        wg_xy_scale_lbl = QtWidgets.QLabel("XY scale:", self)
        wg_xy_shift_lbl = QtWidgets.QLabel("XY shift:", self)

        self.wg_xyscale_mat = [self._make_double_edit(self.xy_scale_changed) for i in range(6)]

        # Labels in row 8
        grid.addWidget(wg_xy_scale_lbl, 8, 0, 1, 2)
        grid.addWidget(wg_xy_shift_lbl, 8, 2)
        # Matrix entries in rows 9, 10
        for i in range(2):
            for j in range(3):
                grid.addWidget(self.wg_xyscale_mat[3 * i + j], 9 + i, j)

        # approximation points
        wg_approx_lbl = QtWidgets.QLabel("Approx. dimensions:")
        grid.addWidget(wg_approx_lbl, 11, 0, 1, 2)
        wg_approx_lbl = QtWidgets.QLabel("Regularization:")
        grid.addWidget(wg_approx_lbl, 11, 2, 1, 1)

        row_nuv = QtWidgets.QHBoxLayout()
        grid.addLayout(row_nuv, 12, 0 , 1, 2)

        self.wg_u_approx = self._make_nuv_edit()
        self.wg_v_approx = self._make_nuv_edit()
        row_nuv.addWidget(QtWidgets.QLabel("u:"))
        row_nuv.addWidget(self.wg_u_approx, stretch=1)
        row_nuv.addWidget(QtWidgets.QLabel("v:"))
        row_nuv.addWidget(self.wg_v_approx, stretch=1)

        self.wg_reg_weight_le = self._make_double_edit(self.set_regularization)
        self.wg_reg_weight_le.setValidator(QtGui.QDoubleValidator())

        grid.addWidget(self.wg_reg_weight_le, 12, 2, 1, 1)

        self.wg_apply_button = self._make_button(
            None, "Apply", 'Compute approximation and save to the surface list.',
            self.apply)

        grid.addWidget(self.wg_apply_button, 13, 2)
        grid.addWidget(self._make_separator(), 14, 0, 1, 3)


        inner_grid = QtWidgets.QGridLayout()

        self.wg_d_elevation = QtWidgets.QLabel("Elevation:", self)
        self.wg_elevation = self._make_read_only_line()
        inner_grid.addWidget(self.wg_d_elevation, 0, 0)
        inner_grid.addWidget(self.wg_elevation, 0, 1)

        self.wg_d_error = QtWidgets.QLabel("Error:", self)
        self.wg_error = self._make_read_only_line()

        inner_grid.addWidget(self.wg_d_error, 0, 2)
        inner_grid.addWidget(self.wg_error, 0, 3)

        grid.addLayout(inner_grid, 15, 0, 1, 3)
        
        self.wg_message = QtWidgets.QLabel("", self)
        self._set_message("")
        grid.addWidget(self.wg_message, 16, 0, 1, 3)

        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 17, 0, 1, 3)
        

        self._fill_forms()

    def get_curr_quad(self):
        """
        Return quad, u, v for grid plot in mainwindow._show_grid."""
        nuv = self.data._nuv
        quad = self.data.get_actual_quad()
        return quad, nuv


    def get_surface_id(self):
        """
        Used to save actual surface idx.
        :return:
        """
        return self.wg_surf_combo.currentIndex()

    @staticmethod
    def get_unique_name(init_name, names):
        """
        # TODO: make this a general function to provide unique default name. have general machanism to this in common. Given a list of names
        # and given a name prefix return a first unique name.
        # usage: get_unique_name(name, [surf.name for surf in surfaces.surfaces])

        :param init_name:
        :param names:
        :return:
        """
        name_set = set(names)
        namebase = name = init_name
        i = 1

        while name in name_set:
            name = namebase + "_" + str(i)
            i += 1
        return name

    def _make_separator(self):
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        return sep

    def _make_button(self, icon_name, text, tooltip, method):
        """
        Make PushButton instance.
        :param icon_name: icon name in global repository.
        :param button text string
        :param tooltip: Tooltip string.
        :param method: Method to call on clicked signal.
        :return: the button object
        """
        button = QtWidgets.QPushButton() # Parent is Grid set in addWidget
        if icon_name is not None:
            button.setIcon(icon.get_app_icon(icon_name))
        if text is not None:
            button.setText(text)
        button.setToolTip(tooltip)
        button.clicked.connect(method)
        return button

    def _make_read_only_line(self):
        le = QtWidgets.QLineEdit()
        le.setReadOnly(True)
        le.setStyleSheet("background-color:#dddddd");
        return le

    def _make_delimiter_combo(self):
        cb = QtWidgets.QComboBox()
        delimiters = [
            ("space/tab", ' \t'),
            ("comma", ","),
            ("semi-comma", ";"),
            ("|","|")
        ]
        for label, delim in delimiters:
            cb.addItem(label, delim)
        cb.currentIndexChanged.connect(self.set_delimiter)
        return cb

    def set_delimiter(self):
        self.data.file_delimiter = self.wg_delimiter_cb.currentData()

    def _make_skip_lines_le(self):
        le = QtWidgets.QLineEdit()
        le.setToolTip("Skip given number of lines at the file beginning.")
        le.editingFinished.connect(self.set_skip_lines)
        validator = QtGui.QIntValidator()
        validator.setBottom(0)
        le.setValidator(validator)
        return le

    def set_skip_lines(self):
        self.data.file_skip_lines = int(self.wg_skip_lines_le.text())


    def _make_double_edit(self, edited_method):
        """
        EditLine box for a double (part of xyscale).
        """
        edit = QtWidgets.QLineEdit()
        edit.editingFinished.connect(edited_method)
        return edit

    def _make_nuv_edit(self):
        """
        EditLine box for a int (part of nuv).
        """
        edit = QtWidgets.QLineEdit()
        edit.editingFinished.connect(self.nuv_changed)
        nuv_validator = QtGui.QIntValidator()
        nuv_validator.setRange(2, 600)
        edit.setValidator(nuv_validator)
        return edit


    def _set_message(self, text):
        self.wg_message.setText(text)
        if text[0:5] == "Error":
            self.setProperty("status", "error")
        if text:
            self.wg_message.setVisible(True)
        else:
            self.wg_message.setVisible(False)

    ####################################################
    # Event handlers

    def set_regularization(self):
        self.data.regularization = self.float_convert(self.wg_reg_weight_le)

    def change_surface(self, new_idx = None):
        """
        Event for changed surface in combo box. Called also when new item is added.
        """
        if new_idx is None:
            new_idx = int(self.wg_surf_combo.currentData())
        if not self.empty_forms():
            self.wg_surf_combo.setCurrentIndex(self.data._idx)
            return
        self.data = SurfFormData.init_from_surface(self.layers.surfaces[new_idx], new_idx)
        self._fill_forms()

    def rm_surface(self):
        assert self.data._idx != -1
        idx = self.wg_surf_combo.currentData()
        assert self.data._idx == idx
        assert idx >= 0
        assert idx < len(self.layers.surfaces)
        if not self.layers.delete_surface(idx):
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog("Surface in use. Can not remove it.")
            return None

        # propose new idx
        new_idx = min(idx, len(self.layers.surfaces) - 1)
        self.data.init_from_surface(self.wg_surf_combo.get_surface(new_idx), new_idx)
        self._fill_forms()


    def add_surface_from_file(self):
        """
        Handle wg_add_button. Open a file and add new unsaved surface into combo and current panel content.
        """
        if not self.empty_forms():
            return
        file, pattern = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose grid file", self.home_dir, "File (*.*)")
        if not file:
            return

        init_name = os.path.basename(file)
        init_name, _ext = os.path.splitext(init_name)
        name = self.get_unique_name(init_name, [surf.name for surf in self.layers.surfaces])

        new_data = SurfFormData()
        new_data.name = name
        new_data.grid_file = file
        new_data.file_skip_lines = self.data.file_skip_lines
        new_data.file_delimiter = self.data.file_delimiter
        data = new_data.init_from_file()
        if data is None:
            # Error in file
            self._set_message("Error: Invalid file.")
        else:
            self.data = data
        self.wg_view_button.setChecked(True)
        self._fill_forms()


    def reload(self):
        file, pattern = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose grid file", self.home_dir, "File (*.*)")
        if not file:
            return
        result = self.data.init_from_file()
        if result is None:
            # Error in file
            self._set_message("Error: Invalid file.")

        self.wg_view_button.setChecked(True)
        self._fill_forms()

    def apply(self):
        """Save changes to file and compute new elevation and error"""
        self.data.compute_approximation()
        self.data.save_to_layers(self.layers)
        self._fill_forms()


    @classmethod
    def set_le_status(cls, le_obj, val):
        le_obj.setProperty("status", val)
        le_obj.style().unpolish(le_obj)
        le_obj.style().polish(le_obj)
        le_obj.update()

    @classmethod
    def float_convert(cls, le_obj):
        try:
            status = "none"
            val = float(le_obj.text())
        except ValueError:
            status = "error"
            val = None
        cls.set_le_status(le_obj, status)
        return val

    @classmethod
    def int_convert(cls, le_obj):
        try:
            return int(le_obj.text())
        except ValueError:
            cls.set_le_status(le_obj, "error")
            return 3

    def nuv_changed(self):
        u = self.int_convert(self.wg_u_approx)
        v = self.int_convert(self.wg_v_approx)
        self.data.set_nuv( (u,v) )
        if self.data._changed_forms:
            self._set_message("There are modified fields.")
        self.show_grid.emit(self.wg_view_button.isChecked())

    def xy_scale_changed(self):
        mat = [self.float_convert(mat_item) for mat_item in self.wg_xyscale_mat]
        if None in mat:
            return
        mat = np.array(mat, dtype=float).reshape(2,3)
        if np.linalg.det(mat[0:2,0:2]) < 1e-16:
            for field in self.wg_xyscale_mat:
                self.set_le_status(field, "error")
            self._set_message("Error: singular transform matrix.")
            return
        self.data.set_xy_transform(mat)
        if self.data._changed_forms:
            self._set_message("There are modified fields.")
        self.show_grid.emit(self.wg_view_button.isChecked())

    ################################

    def empty_forms(self):
        """
        Check to prevent loose of changes stored in actual in self.data.
        """
        if self.data._changed_forms:
            wg_discard = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                  "title", "Discard changes in current surface forms?",
                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if QtWidgets.QMessageBox.Yes != wg_discard.exec():
                return False          # Do nothing.
        return True



    def _fill_forms(self):
        """
        Fill all forms of the surface panel according to self.data
        """
        if self.data.name == "":
            # Empty form
            self.wg_view_button.setEnabled(False)
            self.wg_surf_combo.setEnabled(False)
            self.wg_file_le.setText("")
            self.wg_file_le.setEnabled(False)
            self.wg_rm_button.setEnabled(False)
            self.wg_reload_button.setEnabled(False)
            self.wg_apply_button.setEnabled(False)

            for form in self.wg_xyscale_mat:
                form.setText("")
                form.setEnabled(False)

            self.wg_reg_weight_le.setEnabled(False)
        else:
            self.wg_view_button.setEnabled(True)
            self.wg_view_button.set_icon()

            self.wg_surf_combo.set_items(self.layers.surfaces, self.data._idx, self.data.name)
            self.wg_surf_combo.setEnabled(True)

            self.wg_file_le.setText(self.data.grid_file)
            self.wg_file_le.setEnabled(True)

            if self.data._idx is -1:
                self.wg_rm_button.setEnabled(False)
            else:
                self.wg_rm_button.setEnabled(True)

            self.wg_reload_button.setEnabled(True)
            self.wg_apply_button.setEnabled(True)

            for form, val in zip(self.wg_xyscale_mat, self.data._xy_transform.flat):
                form.setText(str(val))
                form.setEnabled(True)

            self.wg_reg_weight_le.setEnabled(True)
            self.wg_reg_weight_le.setText(str(self.data.regularization))

        if self.data._nuv is None:
            self.wg_u_approx.setText("")
            self.wg_u_approx.setEnabled(False)
            self.wg_v_approx.setText("")
            self.wg_v_approx.setEnabled(False)
        else:
            self.wg_u_approx.setText(str(self.data._nuv[0]))
            self.wg_u_approx.setEnabled(True)
            self.wg_v_approx.setText(str(self.data._nuv[1]))
            self.wg_v_approx.setEnabled(True)

        if self.data._elevation is None:
            self.wg_elevation.setText("")
            self.wg_elevation.setEnabled(False)
        else:
            self.wg_elevation.setText("{:8.2f}".format(self.data._elevation))
            self.wg_elevation.setEnabled(True)

        if self.data.approx_error is None:
            self.wg_error.setText("")
            self.wg_error.setEnabled(False)
        else:
            self.wg_error.setText("{:8.2e}".format(self.data.approx_error))
            self.wg_error.setEnabled(True)

        if self.data._changed_forms:
            self._set_message("There are modified fields.")
        else:
            self._set_message("")










