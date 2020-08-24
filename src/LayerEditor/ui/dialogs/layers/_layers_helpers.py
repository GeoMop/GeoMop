"""
Dialogs for settings text name property or elevation
"""

from gm_base.geomop_dialogs import GMErrorDialog
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from ...data import LayerSplitType
from LayerEditor.leconfig import cfg
import gm_base.b_spline
import numpy as np

class LayersHelpers():

    @staticmethod
    def validate_depth(edit, validator, dialog):
        """
        Try validate elevation parameter. If problem occured,
        display error and return False
        """
        pos = 0
        text = edit.text()
        state =validator.validate(text, pos)[0]
        if state==QtGui.QValidator.Acceptable:                        
            return True
        elif state == QtGui.QValidator.Intermediate:
            error = "Elevation value out of range (%f, %f)."%(validator.bottom(), validator.top())
        else:
            error = "Bad elevation value format" 
        err_dialog = GMErrorDialog(dialog)
        err_dialog.open_error_dialog(error)
        
    @staticmethod
    def split_type_combo(copy_block):
        """Get combo box with layer splitting types """
        combo = QtWidgets.QComboBox()
        combo.addItem("interpolated", LayerSplitType.interpolated)
        if not copy_block:
            combo.addItem("editable", LayerSplitType.editable)
            combo.addItem("split", LayerSplitType.split)
        combo.setCurrentIndex(0)
        return combo
       
    @staticmethod
    def fill_surface(dialog, interface):
        """Return surface"""
        try:
            interface.elevation = float(dialog.elevation.text())
            if dialog.surface is None:
                interface.surface_id = None
                interface.transform_z = (1, 0.0)
                return
            if (dialog.grid.isChecked()):
                interface.surface_id = dialog.surface.currentIndex()
                interface.transform_z = (float(dialog.zscale.text()),
                                         float(dialog.zshift.text()))
            else:
                interface.surface_id = None
                interface.transform_z = (1, 0.0)
                
        except:
            raise ValueError("Invalid surface type")
      
    @staticmethod
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
                
        surfaces = cfg.layers.surfaces
        is_surface = len(surfaces)>0
        dialog.grid = QtWidgets.QRadioButton("Grid")
        dialog.grid.clicked.connect(_enable_controls)
        if not is_surface:
            dialog.surface = None
            dialog.zcoo.setChecked(True)
            dialog.grid.setEnabled(False)
            error = QtWidgets.QLabel("No surface is defined.")
            grid.addWidget(dialog.grid, row+1, 0)
            grid.addWidget(error, row+1, 1, 1, 2)
            return row+2        
        d_surface = QtWidgets.QLabel("Surface:")
        dialog.surface = QtWidgets.QComboBox()            
        for i in range(0, len(surfaces)):            
            label = surfaces[i].name 
            dialog.surface.addItem( label,  i) 
        dialog.surface.currentIndexChanged.connect(_change_surface)        

        grid.addWidget(dialog.grid, row+1, 0)
        grid.addWidget(d_surface, row+1, 1)
        grid.addWidget(dialog.surface, row+1, 2)

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
        
        grid.addWidget(d_zscale, row+2, 1)
        grid.addWidget(dialog.zscale, row+2, 2)
        grid.addWidget(d_zshift, row+3, 1)
        grid.addWidget(dialog.zshift, row+3, 2)
        
        if interface is not None and interface.surface_id is not None:
            dialog.grid.setChecked(True)
        else:
            dialog.zcoo.setChecked(True)
        _enable_controls()
        
        return row+4
