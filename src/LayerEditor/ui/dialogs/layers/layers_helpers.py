"""
Dialogs for settings text name property or depth
"""

from geomop_dialogs import GMErrorDialog
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from ui.data import LayerSplitType
from leconfig import cfg
import b_spline
import bspline as bs

class LayersHelpers():

    @staticmethod
    def validate_depth(edit, validator, dialog):
        """
        Try validate depth parameter. If problem occured,
        display error and return False
        """
        pos = 0
        text = edit.text()
        state =validator.validate(text, pos)[0]
        if state==QtGui.QValidator.Acceptable:                        
            return True
        elif state == QtGui.QValidator.Intermediate:
            error = "Depth value out of range"
        else:
            error = "Bad depth value format" 
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
    def fill_surface(dialog, surface):
        """Return surface"""
        try:
            surface.depth = float(dialog.depth.text())
            if (dialog.grid.isChecked()):
                surface.grid_file = dialog.file_name.text()
            else:
                surface.grid_file = None
            surface.transform_xy = ((float(dialog.xyscale11.text()), 
                float(dialog.xyscale12.text()), float(dialog.xyscale21.text())), 
                (float(dialog.xyscale22.text()), float(dialog.xyshift1.text()), 
                float(dialog.xyshift2.text())))
            surface.transform_z = (float(dialog.zscale.text()), 
                float(dialog.zshift.text()))
            return surface
        except:
            raise ValueError("Invalid surface type")
      
    @staticmethod
    def add_surface_to_grid(dialog, grid, row, surface=None):
        """Add surface structure to grid"""
        
        def _enable_controls():
            """Disable all not used controls"""
            dialog.depth.setEnabled(dialog.zcoo.isChecked())
            
            dialog.file_name.setEnabled(dialog.grid.isChecked())
            dialog.file_button.setEnabled(dialog.grid.isChecked())
            dialog.xyscale11.setEnabled(dialog.grid.isChecked())
            dialog.xyscale12.setEnabled(dialog.grid.isChecked())
            dialog.xyscale21.setEnabled(dialog.grid.isChecked())
            dialog.xyscale22.setEnabled(dialog.grid.isChecked())
            dialog.xyshift1.setEnabled(dialog.grid.isChecked())
            dialog.xyshift2.setEnabled(dialog.grid.isChecked())
            dialog.zscale.setEnabled(dialog.grid.isChecked())
            dialog.zshift.setEnabled(dialog.grid.isChecked())
            
        dialog.zcoo = QtWidgets.QRadioButton("Z-Coordinate:")
        dialog.zcoo.clicked.connect(_enable_controls)
        d_depth = QtWidgets.QLabel("Depth:", dialog)
        dialog.depth = QtWidgets.QLineEdit() 
        if surface is not None:
            dialog.depth.setText(str(surface.depth))
        
        grid.addWidget(dialog.zcoo, row, 0)
        grid.addWidget(d_depth, row, 1)
        grid.addWidget(dialog.depth, row, 2)
        
        def _add_file():
            """Clicked event for _file_button"""
            home = cfg.config.data_dir
            file = QtWidgets.QFileDialog.getOpenFileName(
                dialog, "Choose grif file", home,"File (*.*)")
            if file[0]:
                gs = bs.GridSurface.load(file[0])
                center = gs.center()
                dialog.depth_value = -center[2]
                dialog.file_name.setText(file[0])
                _compute_depth()
        
        dialog.grid = QtWidgets.QRadioButton("Grid")
        dialog.grid.clicked.connect(_enable_controls)
        d_file = QtWidgets.QLabel("File:")
        dialog.file_name = QtWidgets.QLineEdit()
        dialog.file_name.setReadOnly(True)
        dialog.file_button = QtWidgets.QPushButton("...")
        dialog.file_button.clicked.connect(_add_file)
        if surface is not None:
            dialog.file_name.setText(surface.grid_file)

        grid.addWidget(dialog.grid, row+1, 0)
        grid.addWidget(d_file, row+1, 1)
        grid.addWidget(dialog.file_name, row+1, 2, 1, 3)        
        grid.addWidget(dialog.file_button, row+1, 5)
        
        d_xyscale = QtWidgets.QLabel("XY scale:", dialog)
        dialog.xyscale11 = QtWidgets.QLineEdit()
        dialog.xyscale11.setValidator(QtGui.QDoubleValidator())
        dialog.xyscale11.setText("1.0")
        dialog.xyscale12 = QtWidgets.QLineEdit()
        dialog.xyscale12.setValidator(QtGui.QDoubleValidator())
        dialog.xyscale12.setText("0.0")
        dialog.xyscale21 = QtWidgets.QLineEdit()
        dialog.xyscale21.setValidator(QtGui.QDoubleValidator())
        dialog.xyscale21.setText("0.0")
        dialog.xyscale22 = QtWidgets.QLineEdit()
        dialog.xyscale22.setValidator(QtGui.QDoubleValidator())
        dialog.xyscale22.setText("1.0")
        
        if surface is not None:
            dialog.xyscale11.setText(str(surface.transform_xy[0][0]))
            dialog.xyscale12.setText(str(surface.transform_xy[0][1]))
            dialog.xyscale21.setText(str(surface.transform_xy[1][0]))
            dialog.xyscale22.setText(str(surface.transform_xy[1][1]))
        
        d_xyshift = QtWidgets.QLabel("XY shift:", dialog)        
        dialog.xyshift1 = QtWidgets.QLineEdit()
        dialog.xyshift1.setValidator(QtGui.QDoubleValidator())
        dialog.xyshift1.setText("0.0")
        dialog.xyshift2 = QtWidgets.QLineEdit()
        dialog.xyshift2.setValidator(QtGui.QDoubleValidator())
        dialog.xyshift2.setText("0.0")
        
        if surface is not None:
            dialog.xyshift1.setText(str(surface.transform_xy[0][2]))
            dialog.xyshift2.setText(str(surface.transform_xy[1][2]))        
        
        grid.addWidget(d_xyscale, row+2, 1)
        grid.addWidget(dialog.xyscale11, row+2, 2)
        grid.addWidget(dialog.xyscale21, row+2, 3)
        grid.addWidget(d_xyshift, row+2, 4)
        grid.addWidget(dialog.xyshift1, row+2, 5)
        
        grid.addWidget(dialog.xyscale12, row+3, 2)
        grid.addWidget(dialog.xyscale22, row+3, 3)
        grid.addWidget(dialog.xyshift2, row+3, 5)
        
        d_zscale = QtWidgets.QLabel("Z scale:", dialog)
        dialog.zscale = QtWidgets.QLineEdit()
        dialog.zscale.setValidator(QtGui.QDoubleValidator())
        dialog.zscale.setText("1.0")  
        dialog.depth_value = 0
        
        def _compute_depth():
            """Compute depth for grid file"""
            grid_file = dialog.file_name.text()
            if dialog.grid.isChecked() and \
                len(grid_file)>0 and not grid_file.isspace():
                try:
                    z=float(dialog.zshift.text())
                except:
                    z=0
                depth = dialog.depth_value + z
                dialog.depth.setText(str(depth))

        d_zshift = QtWidgets.QLabel("Z shift:", dialog)
        dialog.zshift = QtWidgets.QLineEdit()
        dialog.zshift.setValidator(QtGui.QDoubleValidator())
        dialog.zshift.setText("1.0")
        dialog.zshift.textChanged.connect(_compute_depth)        
        
        if surface is not None:
            dialog.zscale.setText(str(surface.transform_z[0]))
            dialog.zshift.setText(str(surface.transform_z[1]))
        
        grid.addWidget(d_zscale, row+4, 1)
        grid.addWidget(dialog.zscale, row+4, 2)
        grid.addWidget(d_zshift, row+4, 4)
        grid.addWidget(dialog.zshift, row+4, 5)
        
        if surface is not None and surface.grid_file is not None and \
            len(surface.grid_file) and not surface.grid_file.isspace():
            dialog.grid.setChecked(True)
            gs = bs.GridSurface.load(surface.grid_file)
            center = gs.center()
            dialog.depth_value = -center[2]
            _compute_depth()
        else:
            dialog.zcoo.setChecked(True)
        _enable_controls()
        
        return row+5
