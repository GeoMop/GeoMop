import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import logging

import os
import numpy as np
import copy
import shutil

from LayerEditor.ui.data.le_model import LEModel
from LayerEditor.ui.data.surface_item import SurfaceItem
from LayerEditor.ui.data.surface_item_draft import SurfaceItemDraft
from LayerEditor.widgets.line_edit import LineEdit
from LayerEditor.widgets.text_validator import NameValidator
from bgem.bspline import bspline_approx as ba
from gm_base.geomop_dialogs import GMErrorDialog
import gm_base.icon as icon
import gm_base.geometry_files.format_last as GL
from LayerEditor.data import cfg

"""
TODO:
Why is approx error so large. Debug display error distribution.
"""


class SurfacesComboBox(QtWidgets.QComboBox):
    def __init__(self, parent):
        super().__init__()
        self._parent = parent
        self.setEditable(True)
        self.setEnabled(False)
        self.setLineEdit(LineEdit())
        self.setCompleter(None)
        self.lineEdit().textEdited.connect(self.text_changed)
        self.lineEdit().editingFinished.connect(self.edit_finished)
        self.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.setValidator(NameValidator(self.unique_name_fnc,
                                        lambda: self.itemText(self.currentIndex())))

    def unique_name_fnc(self, new_name):
        for surf in self._parent.le_model.surfaces_model.items():
            if surf.name == new_name:
                return False
        return True

    def set_items(self, surfaces, new_idx=0, name=""):
        self.blockSignals(True)
        self.clear()
        for idx, surf in enumerate(surfaces):
            self.addItem(surf.name,  idx)
        if new_idx == -1:
            self.addItem(name, -1)
            new_idx = self.count() - 1
            self.setCurrentIndex(new_idx)
        self.blockSignals(False)

    def text_changed(self, new_name):
        valid = self.lineEdit().validator().validate(new_name, self.lineEdit().cursorPosition())[0]
        if valid is QtGui.QValidator.Acceptable:
            self.lineEdit().mark_text_valid()
            self.lineEdit().setToolTip("")
        else:
            self.lineEdit().mark_text_invalid()
            self.lineEdit().setToolTip("This name already exist")

    def edit_finished(self):
        new_name = self.currentText()
        self.lineEdit().mark_text_valid()
        valid = self.lineEdit().validator().validate(new_name, self.lineEdit().cursorPosition())[0]
        if valid is QtGui.QValidator.Acceptable and new_name != self._parent.data.name:
            self.setItemText(self.currentIndex(), new_name)
            self._parent.data.set_name(new_name)


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


class Surfaces(QtWidgets.QWidget):
    """
    GeoMop Layer editor surfaces panel
    
    pyqtSignals:
        * :py:attr:`show_grid
    """
    show_grid = QtCore.pyqtSignal(bool)
    """Signal is sent when mash should be shown or repaint.    
    :param bool force: if force not set, don't call mash if already exist
    """
    first_surface_added = QtCore.pyqtSignal(QtCore.QRectF)
    """ Signal for changing init area rect based on first loaded surface.
        :param QRectF init_area: area of the first surface
    """

    def __init__(self, le_model, save_fnc, parent=None):
        """
        :param le_model: LEModel data object (i.e. parent data object where we may read and write the data)
        :param parent: Surface panel parent.
        """
        super().__init__(parent)
        self.save_fnc = save_fnc
        # Data class for the surface panel.
        # This is copy of one of surfaces in LEData or default SurfaceItem if no surface exists.
        self.data = SurfaceItemDraft()
        if le_model.gui_surface_selector.value is not None:
            curr_surf = le_model.gui_surface_selector.value
            self.data.update_from_surface(curr_surf)
        # Surfaces list in LEModel.
        self.le_model = le_model

        # Setup child widgets
        grid = QtWidgets.QGridLayout(self)
        self.setLayout(grid)

        surf_row = QtWidgets.QHBoxLayout()

        wg_suface_lbl = QtWidgets.QLabel("Surface:")
        grid.addWidget(wg_suface_lbl, 0, 0, 1, 3)
        grid.addLayout(surf_row, 1, 0, 1, 3)

        self.wg_view_button = WgShowButton("Switch visibilty of the surface grid.", parent=self)
        self.wg_view_button.toggled.connect(self.show_grid)
        if self.le_model.gui_surface_selector.value is not None:
            self.wg_view_button.setChecked(True)

        # surface combobox
        self.wg_surf_combo = SurfacesComboBox(self)
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
        self.set_delimiter()

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
        wg_approx_lbl = QtWidgets.QLabel("Tolerance:")
        grid.addWidget(wg_approx_lbl, 11, 2, 1, 1)

        row_nuv = QtWidgets.QHBoxLayout()
        grid.addLayout(row_nuv, 12, 0 , 1, 2)

        self.wg_u_approx = self._make_nuv_edit()
        self.wg_v_approx = self._make_nuv_edit()
        row_nuv.addWidget(QtWidgets.QLabel("u:"))
        row_nuv.addWidget(self.wg_u_approx, stretch=1)
        row_nuv.addWidget(QtWidgets.QLabel("v:"))
        row_nuv.addWidget(self.wg_v_approx, stretch=1)

        self.wg_tolerance_le = self._make_double_edit(self.set_tolerance)
        self.wg_tolerance_le.setValidator(QtGui.QDoubleValidator())

        grid.addWidget(self.wg_tolerance_le, 12, 2, 1, 1)

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

        wg_actual_dim_lbl = QtWidgets.QLabel("Actual dimensions:")
        inner_grid.addWidget(wg_actual_dim_lbl, 1, 0, 1, 2)

        row_actual_nuv = QtWidgets.QHBoxLayout()
        inner_grid.addLayout(row_actual_nuv, 2, 0 , 1, 4)

        self.wg_actual_u = self._make_read_only_line()
        self.wg_actual_v = self._make_read_only_line()
        row_actual_nuv.addWidget(QtWidgets.QLabel("u:"))
        row_actual_nuv.addWidget(self.wg_actual_u, stretch=1)
        row_actual_nuv.addWidget(QtWidgets.QLabel("v:"))
        row_actual_nuv.addWidget(self.wg_actual_v, stretch=1)

        grid.addLayout(inner_grid, 15, 0, 1, 3)
        
        self.wg_message = QtWidgets.QLabel("", self)
        self._set_message("")
        grid.addWidget(self.wg_message, 16, 0, 1, 3)

        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 17, 0, 1, 3)

        self.update_forms()

    def get_curr_quad(self):
        """
        Return quad, u_knots, v_knots for grid plot in mainwindow._show_grid."""
        approx = self.data.approximation
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
        quad = self.data.get_actual_quad()
        return quad, u_knots, v_knots

    def get_surface_id(self):
        """
        Used to save actual surface idx.
        :return:
        """
        return self.wg_surf_combo.currentIndex()

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
            ("space/tab", '[ \t]'),
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
        nuv_validator.setRange(1, 999)
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

    def set_tolerance(self):
        self.data.tolerance = self.float_convert(self.wg_tolerance_le)

    def change_surface(self, new_idx=None):
        """
        Event for changed surface in combo box. Called also when new item is added.
        """
        if new_idx is None\
                or not (0 < new_idx < len(self.le_model.surfaces_model)):
            new_idx = self.wg_surf_combo.currentData()

        if not self.empty_forms():
            surfaces = self.le_model.surfaces_model.sorted_items_elevation()
            idx = self.data.get_copied_from_index(surfaces)
            idx = idx if idx != -1 else len(surfaces)
            self.wg_surf_combo.blockSignals(True)
            self.wg_surf_combo.setCurrentIndex(idx)
            self.wg_surf_combo.blockSignals(False)
            return
        if new_idx is not None:
            surfaces = self.le_model.surfaces_model.sorted_items_elevation()
            new_surf = surfaces[new_idx]
            self.data = SurfaceItemDraft()
            self.data.copy_from_surface_item(new_surf)
        self.update_forms()
        self.show_grid.emit(self.wg_view_button.isChecked())

    def rm_surface(self):
        assert self.data.copied_from is not None
        idx = self.wg_surf_combo.currentData()
        assert self.data.get_index_from_list(self.le_model.surfaces_model.sorted_items_elevation()) == idx
        assert idx >= 0
        assert idx < len(self.le_model.surfaces_model)
        if not self.le_model.delete_surface(idx):
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog("Surface in use. Can not remove it.")
            return None

        # propose new idx
        new_idx = min(idx, len(self.le_model.surfaces_model) - 1)
        self.data = SurfaceItemDraft()
        self.data.copy_from_surface_item(self.e_model.surfaces_model.sorted_items_elevation()[new_idx])

        self.update_forms()
        self.show_grid.emit(self.wg_view_button.isChecked())

    def add_surface_from_file(self):
        """
        Handle wg_add_button. Open a file and add new unsaved surface into combo and current panel content.
        """
        if not self.empty_forms():
            return
        new_data = SurfaceItemDraft()
        new_data.file_skip_lines = self.data.file_skip_lines
        new_data.file_delimiter = self.data.file_delimiter
        data = self._load_file(new_data)
        if data:
            if not self.le_model.surfaces_model:
                quad = new_data.get_actual_quad()
                points = [QtCore.QPointF(point[0], -point[1]) for point in quad]
                points.append(QtCore.QPointF(quad[0][0], -quad[0][1]))
                rect = QtGui.QPolygonF(points).boundingRect()
                x_adjust = rect.width() / 6
                y_adjust = rect.height() / 6
                rect.adjust(-x_adjust, -y_adjust, x_adjust, y_adjust)
                self.first_surface_added.emit(rect)
            new_data.set_name_from_file(self.le_model)
            self.data = new_data
            self.wg_view_button.setChecked(True)
        self.update_forms()
        self.show_grid.emit(self.wg_view_button.isChecked())

    def reload(self):
        self._load_file(self.data)
        self.wg_view_button.setChecked(True)
        self.update_forms()

    def _load_file(self, surface_data):
        # save layer data first
        if self.le_model.curr_file is None:
            QtWidgets.QMessageBox.information(
                self, 'Save layer data',
                'Layer data file must be save first.')
            self.save_fnc()
        if self.le_model.curr_file is None:
            return

        file, pattern = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose grid file", cfg.current_workdir, "File (*.*)")
        if not file:
            return

        file = self._check_file_path(file)
        if not file:
            return

        try:
            cfg.update_current_workdir(file)
            return surface_data.init_from_file(file)
        except Exception as e:
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog("Wrong grid file structure!", error=e)
            return None

    def _check_file_path(self, file):
        """
        Check if file is in project directory.
        If not try copy it.
        Returns new path or empty string if it is not possible.
        """
        layer_file_dir = os.path.dirname(self.le_model.curr_file)
        relpath = os.path.relpath(file, start=layer_file_dir)
        if relpath.startswith("../") or (os.sep == "\\" and relpath.startswith("..\\")):
            basename = os.path.basename(file)
            path_in_dir = os.path.join(layer_file_dir, basename)
            if os.path.exists(path_in_dir):
                QtWidgets.QMessageBox.critical(
                    self, 'File already exists',
                    'File "{}" already exists in project directory.'.format(basename))
                return ""

            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle("Copy file")
            msg.setText('File must be in project directory.\n'
                        "Do you want to copy it?")
            msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            msg.setDefaultButton(QtWidgets.QMessageBox.Yes)
            ret = msg.exec()
            if ret == QtWidgets.QMessageBox.Yes:
                shutil.copyfile(file, path_in_dir)
                return path_in_dir
            else:
                return ""

        return file

    def apply(self):
        """Save changes to file and compute new elevation and error"""
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                    "Computing...",
                                    "Computing approximation.\nPlease wait.")
        msg.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        msg.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        msg.setWindowModality(QtCore.Qt.WindowModal)
        msg.show()
        QtWidgets.QApplication.processEvents()

        # log = logging.getLogger()
        # log.setLevel(logging.INFO)
        # handler = logging.StreamHandler()
        # handler.setLevel(logging.INFO)
        # log.addHandler(handler)

        self.data.compute_approximation()

        QtWidgets.QApplication.processEvents()
        msg.hide()

        new_surface = self.data.save_to_le_model(self.le_model)
        self.update_forms()
        self.le_model.gui_surface_selector.value = new_surface
        self.show_grid.emit(self.wg_view_button.isChecked())

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
        self.data.set_nuv((u, v))
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

    def update_forms(self):
        """
        Fill all forms of the surface panel according to self.data
        """
        if self.data.name == "":
            # Empty form
            self.wg_view_button.setEnabled(False)
            self.wg_surf_combo.clear()
            self.wg_surf_combo.setEnabled(False)
            self.wg_file_le.setText("")
            self.wg_file_le.setEnabled(False)
            self.wg_rm_button.setEnabled(False)
            self.wg_reload_button.setEnabled(False)
            self.wg_apply_button.setEnabled(False)

            for form in self.wg_xyscale_mat:
                form.setText("")
                form.setEnabled(False)

            self.wg_tolerance_le.setEnabled(False)

            self.wg_u_approx.setText("")
            self.wg_u_approx.setEnabled(False)
            self.wg_v_approx.setText("")
            self.wg_v_approx.setEnabled(False)
        else:
            self.wg_view_button.setEnabled(True)
            self.wg_view_button.set_icon()

            surfaces = self.le_model.surfaces_model.sorted_items_elevation()
            idx = self.data.get_copied_from_index(surfaces)
            self.wg_surf_combo.set_items(surfaces, idx, self.data.name)
            self.wg_surf_combo.setEnabled(True)

            self.wg_file_le.setText(self.data.grid_file)
            self.wg_file_le.setEnabled(True)

            if self.data.copied_from is None:
                self.wg_rm_button.setEnabled(False)
            else:
                self.wg_rm_button.setEnabled(True)

            self.wg_reload_button.setEnabled(True)
            self.wg_apply_button.setEnabled(True)

            for form, val in zip(self.wg_xyscale_mat, np.array(self.data.xy_transform, dtype = float).flat):
                form.setText(str(val))
                form.setEnabled(True)

            self.wg_tolerance_le.setEnabled(True)
            self.wg_tolerance_le.setText(str(self.data.tolerance))

            if self.data.nuv is not None:
                self.wg_u_approx.setText(str(self.data.nuv[0]))
                self.wg_u_approx.setEnabled(True)
                self.wg_v_approx.setText(str(self.data.nuv[1]))
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

        if self.data.approximation is not None:
            u = self.data.approximation.u_basis.n_intervals
            v = self.data.approximation.v_basis.n_intervals
            self.wg_actual_u.setText(str(u))
            self.wg_actual_v.setText(str(v))
        else:
            self.wg_actual_u.setText("")
            self.wg_actual_v.setText("")

