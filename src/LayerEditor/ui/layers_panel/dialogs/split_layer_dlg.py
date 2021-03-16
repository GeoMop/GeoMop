"""
Dialog for appending new layer to the end.
"""
import math
import numpy as np

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from PyQt5.QtCore import Qt, QPoint

import gm_base.icon as icon
from LayerEditor.ui.layers_panel import helper_functions


class SplitLayerDlg(QtWidgets.QDialog):

    def __init__(self, top_y, bot_y, le_model, parent=None):
        super(SplitLayerDlg, self).__init__(parent)
        self.fnc_get_default_layer_name = le_model.get_default_layer_name
        self.fnc_sorted_items_elevation = le_model.surfaces_model.sorted_items_elevation
        self.fnc_is_layer_name_unique = le_model.is_layer_name_unique
        self.top_y = top_y if top_y is not None else math.inf
        self.bot_y = bot_y if bot_y is not None else -math.inf

        if top_y is None:
            default_elevation = bot_y + 100
        elif bot_y is None:
            default_elevation = top_y - 100
        else:
            default_elevation = (top_y + bot_y) / 2

        self.red_palette = QtGui.QPalette()
        self.red_palette.setColor(QtGui.QPalette.Text, Qt.red)

        self.default_palette = self.palette()

        self.setWindowTitle("Split Layer")

        grid = QtWidgets.QGridLayout(self)

        d_layer_name = QtWidgets.QLabel("Layer Name:", self)
        self.layer_name = QtWidgets.QLineEdit(self.fnc_get_default_layer_name("Layer"))
        self.layer_name.setToolTip("New Layer name")
        self.layer_name.textChanged.connect(self.layer_name_changed)

        self.name_image = QtWidgets.QLabel(self)
        self.name_image.setMinimumWidth(self.layer_name.sizeHint().height())
        self.name_image.setPixmap(icon.get_app_icon("sign-check").pixmap(self.layer_name.sizeHint().height()))
        self.name_image.setToolTip('Layer name is unique, everything is fine.')

        grid.addWidget(d_layer_name, 0, 0)
        grid.addWidget(self.layer_name, 0, 2)
        grid.addWidget(self.name_image, 0, 3)
        
        # d_split_type = QtWidgets.QLabel("Split Interface Type:", self)
        # combo = QtWidgets.QComboBox()
        # combo.addItem("interpolated")
        
        # grid.addWidget(d_split_type, 1, 0)
        # grid.addWidget(combo, 1, 1)
        
        d_surface = QtWidgets.QLabel("Split in Surface:", self)
        grid.addWidget(d_surface, 2, 0)
        self.add_surface_to_grid(grid, 3)

        self.elevation_image = QtWidgets.QLabel(self)
        self.elevation_image.setMinimumWidth(self.layer_name.sizeHint().height())
        self.elevation_image.setPixmap(icon.get_app_icon("sign-check").pixmap(self.layer_name.sizeHint().height()))
        self.elevation_image.setToolTip('Layer name is unique, everything is fine.')

        grid.addWidget(self.elevation_image, 3, 3)

        self.elevation.setText(str(default_elevation))
        
        self._tranform_button = QtWidgets.QPushButton("Split", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, grid.rowCount(), 1, 1, 3)
        self.setLayout(grid)
        self.elevation.textChanged.connect(self.elevation_changed)

    def add_surface_to_grid(self, grid, row, interface=None):
        """Add surface structure to grid"""

        def _enable_controls():
            """Disable all not used controls"""
            if self.surface is None:
                return
            self.elevation.setEnabled(self.zcoo.isChecked())
            self.surface.setEnabled(self.grid.isChecked())
            self.zscale.setEnabled(self.grid.isChecked())
            self.zshift.setEnabled(self.grid.isChecked())

            if self.grid.isChecked():
                _change_surface()

        self.zs = None
        self.zcoo = QtWidgets.QRadioButton("Z-Coordinate:")
        self.zcoo.clicked.connect(_enable_controls)
        d_depth = QtWidgets.QLabel("Elevation:", self)
        self.elevation = QtWidgets.QLineEdit()
        if interface is not None:
            self.elevation.setText(str(interface.elevation))

        grid.addWidget(self.zcoo, row, 0)
        grid.addWidget(d_depth, row, 1)
        grid.addWidget(self.elevation, row, 2)

        def _change_surface():
            """Changed event for surface ComboBox"""
            id = self.surface.currentIndex()
            self.zs = surfaces[id].approximation
            _compute_depth()

        surfaces = self.fnc_sorted_items_elevation()
        is_surface = len(surfaces) > 0
        self.grid = QtWidgets.QRadioButton("Grid")
        self.grid.clicked.connect(_enable_controls)
        if not is_surface:
            self.surface = None
            self.zcoo.setChecked(True)
            self.grid.setEnabled(False)
            error = QtWidgets.QLabel("No surface is defined.")
            grid.addWidget(self.grid, row + 1, 0)
            grid.addWidget(error, row + 1, 1, 1, 2)
            return row + 2
        d_surface = QtWidgets.QLabel("Surface:")
        self.surface = QtWidgets.QComboBox()
        for i in range(0, len(surfaces)):
            label = surfaces[i].name
            self.surface.addItem(label, i)
        self.surface.currentIndexChanged.connect(_change_surface)

        grid.addWidget(self.grid, row + 1, 0)
        grid.addWidget(d_surface, row + 1, 1)
        grid.addWidget(self.surface, row + 1, 2)

        d_zscale = QtWidgets.QLabel("Z scale:", self)
        self.zscale = QtWidgets.QLineEdit()
        self.zscale.setValidator(QtGui.QDoubleValidator())
        self.zscale.setText("1.0")
        self.depth_value = 0

        def _compute_depth():
            """Compute elevation for grid file"""
            if self.zs is None:
                return
            try:
                z1 = float(self.zscale.text())
            except:
                z1 = 0
            try:
                z2 = float(self.zshift.text())
            except:
                z2 = 0
            self.zs.transform(None, np.array([z1, z2], dtype=float))
            center = self.zs.center()
            self.elevation.setText(str(center[2]))

        d_zshift = QtWidgets.QLabel("Z shift:", self)
        self.zshift = QtWidgets.QLineEdit()
        self.zshift.setValidator(QtGui.QDoubleValidator())
        self.zshift.setText("0.0")
        self.zshift.textChanged.connect(_compute_depth)

        if interface is not None and interface.surface_id is not None:
            self.surface.setCurrentIndex(interface.surface_id)

        if interface is not None and interface.transform_z:
            self.zscale.setText(str(interface.transform_z[0]))
            self.zshift.setText(str(interface.transform_z[1]))

        grid.addWidget(d_zscale, row + 2, 1)
        grid.addWidget(self.zscale, row + 2, 2)
        grid.addWidget(d_zshift, row + 3, 1)
        grid.addWidget(self.zshift, row + 3, 2)

        if interface is not None and interface.surface_id is not None:
            self.grid.setChecked(True)
        else:
            self.zcoo.setChecked(True)
        _enable_controls()

        return row + 4

    def layer_name_changed(self, name):
        """ Called when Region Line Edit is changed."""
        if self.fnc_is_layer_name_unique(name):
            self.name_image.setPixmap(
                icon.get_app_icon("sign-check").pixmap(self.layer_name.sizeHint().height())
            )
            self.name_image.setToolTip('Unique name is OK.')
        else:
            self.name_image.setPixmap(
                icon.get_app_icon("warning").pixmap(self.layer_name.sizeHint().height())
            )
            self.name_image.setToolTip('Name is not unique!')
        self._tranform_button.setEnabled(self.everything_ok())

    def elevation_changed(self):
        if self.elevation_ok():
            self.elevation_image.setPixmap(
                icon.get_app_icon("sign-check").pixmap(self.layer_name.sizeHint().height()))
        else:
            self.elevation_image.setPixmap(
                icon.get_app_icon("warning").pixmap(self.layer_name.sizeHint().height()))

        self._tranform_button.setEnabled(self.everything_ok())

    def elevation_ok(self):
        try:
            elevation = float(self.elevation.text())
        except ValueError:
            self.elevation_image.setToolTip("Invalid number format!")
            return False

        if self.top_y > elevation > self.bot_y:
            self.elevation_image.setToolTip("Elevation OK.")
            return True
        else:
            self.elevation_image.setToolTip("This layer can be only split from {} to {}".format(self.top_y, self.bot_y))
            return False

    def everything_ok(self):
        if self.elevation_ok() and self.fnc_is_layer_name_unique(self.layer_name.text()):
            return True
        else:
            return False


