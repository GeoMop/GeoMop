from PyQt5 import QtWidgets, QtGui
import numpy as np


def add_surface_to_grid(dialog, grid, row, interface=None):
    """Add surface structure to grid"""

    def _enable_controls():
        """Disable all not used controls"""
        if dialog.surface is None:
            return
        dialog.elevation.setEnabled(dialog.zcoo.isChecked())
        dialog.surface.setEnabled(dialog.grid.isChecked())
        dialog.zscale.setEnabled(dialog.grid.isChecked())
        dialog.zshift.setEnabled(dialog.grid.isChecked())

        if dialog.grid.isChecked():
            _change_surface()

    dialog.zs = None
    dialog.zcoo = QtWidgets.QRadioButton("Z-Coordinate:")
    dialog.zcoo.clicked.connect(_enable_controls)
    d_depth = QtWidgets.QLabel("Elevation:", dialog)
    dialog.elevation = QtWidgets.QLineEdit()
    if interface is not None:
        dialog.elevation.setText(str(interface.elevation))

    grid.addWidget(dialog.zcoo, row, 0)
    grid.addWidget(d_depth, row, 1)
    grid.addWidget(dialog.elevation, row, 2)

    def _change_surface():
        """Changed event for surface ComboBox"""
        id = dialog.surface.currentIndex()
        dialog.zs = surfaces[id].approximation
        _compute_depth()

    surfaces = dialog.le_model.surfaces_model.sorted_items_elevation()
    is_surface = len(surfaces ) >0
    dialog.grid = QtWidgets.QRadioButton("Grid")
    dialog.grid.clicked.connect(_enable_controls)
    if not is_surface:
        dialog.surface = None
        dialog.zcoo.setChecked(True)
        dialog.grid.setEnabled(False)
        error = QtWidgets.QLabel("No surface is defined.")
        grid.addWidget(dialog.grid, row +1, 0)
        grid.addWidget(error, row +1, 1, 1, 2)
        return row + 2
    d_surface = QtWidgets.QLabel("Surface:")
    dialog.surface = QtWidgets.QComboBox()
    for i in range(0, len(surfaces)):
        label = surfaces[i].name
        dialog.surface.addItem( label,  i)
    dialog.surface.currentIndexChanged.connect(_change_surface)

    grid.addWidget(dialog.grid, row + 1, 0)
    grid.addWidget(d_surface, row + 1, 1)
    grid.addWidget(dialog.surface, row + 1, 2)

    d_zscale = QtWidgets.QLabel("Z scale:", dialog)
    dialog.zscale = QtWidgets.QLineEdit()
    dialog.zscale.setValidator(QtGui.QDoubleValidator())
    dialog.zscale.setText("1.0")
    dialog.depth_value = 0

    def _compute_depth():
        """Compute elevation for grid file"""
        if dialog.zs is None:
            return
        try:
            z1 = float(dialog.zscale.text())
        except:
            z1 = 0
        try:
            z2 = float(dialog.zshift.text())
        except:
            z2 = 0
        dialog.zs.transform(None, np.array([z1, z2], dtype=float))
        center = dialog.zs.center()
        dialog.elevation.setText(str(center[2]))

    d_zshift = QtWidgets.QLabel("Z shift:", dialog)
    dialog.zshift = QtWidgets.QLineEdit()
    dialog.zshift.setValidator(QtGui.QDoubleValidator())
    dialog.zshift.setText("0.0")
    dialog.zshift.textChanged.connect(_compute_depth)

    if interface is not None and interface.surface_id is not None:
        dialog.surface.setCurrentIndex(interface.surface_id)

    if interface is not None and interface.transform_z:
        dialog.zscale.setText(str(interface.transform_z[0]))
        dialog.zshift.setText(str(interface.transform_z[1]))

    grid.addWidget(d_zscale, row + 2, 1)
    grid.addWidget(dialog.zscale, row + 2, 2)
    grid.addWidget(d_zshift, row + 3, 1)
    grid.addWidget(dialog.zshift, row + 3, 2)

    if interface is not None and interface.surface_id is not None:
        dialog.grid.setChecked(True)
    else:
        dialog.zcoo.setChecked(True)
    _enable_controls()

    return row + 4