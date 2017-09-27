"""
Dialogs for settings text name property or depth
"""

from geomop_dialogs import GMErrorDialog
import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
from ui.data import LayerSplitType
from leconfig import cfg

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
            surface.grid_file = dialog.file_name.text()
            surface.transform_xy[0][0] = float(dialog.dialog.xyscale11.text())
            surface.transform_xy[0][1] = float(dialog.dialog.xyscale12.text())
            surface.transform_xy[1][0] = float(dialog.dialog.xyscale21.text())
            surface.transform_xy[1][1] = float(dialog.dialog.xyscale22.text())
            surface.transform_xy[0][2] = float(dialog.dialog.xyshift1.text())
            surface.transform_xy[1][2] = float(dialog.dialog.xyshift2.text())
            surface.transform_z[0] = float(dialog.dialog.zscale.text())
            surface.transform_z[2] = float(dialog.dialog.zshift.text())
            return surface
        except:
            raise ValueError("Invalid depth type")
      
    @staticmethod
    def add_surface_to_grid(dialog, grid, row, surface=None):
        """Add surface structure to grid"""
        d_depth = QtWidgets.QLabel("Depth:", dialog)
        dialog.depth = QtWidgets.QLineEdit() 
        if surface is not None:
            dialog.depth.setText(str(surface.depth))
        
        grid.addWidget(d_depth, row, 0)
        grid.addWidget(dialog.depth, row, 1)
        
        def _add_file(self):
            """Clicked event for _file_button"""
            home = cfg.config.data_dir
            file = QtWidgets.QFileDialog.getOpenFileName(
                dialog, "Choose grif file", home,"File (*.*)")
            if file[0]:
                self._file_name.setText(file[0])
                
        d_file = QtWidgets.QLabel("Grid File:")
        dialog.file_name = QtWidgets.QLineEdit()
        dialog.file_button = QtWidgets.QPushButton("...")
        dialog.file_button.clicked.connect(_add_file)
        if surface is not None:
            dialog.file_name.setText(surface.grid_file)

        grid.addWidget(d_file, row+1, 0)
        grid.addWidget(dialog.file_name, row+1, 1)        
        grid.addWidget(dialog.file_button, row+1, 2)
        
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
        
        grid.addWidget(d_xyscale, row+2, 0)
        grid.addWidget(dialog.xyscale11, row+2, 1)
        grid.addWidget(dialog.xyscale21, row+2, 2)
        grid.addWidget(d_xyshift, row+2, 3)
        grid.addWidget(dialog.xyshift1, row+2, 4)
        
        grid.addWidget(dialog.xyscale12, row+3, 1)
        grid.addWidget(dialog.xyscale22, row+3, 2)
        grid.addWidget(dialog.xyshift2, row+3, 4)
        
        d_zscale = QtWidgets.QLabel("Z scale:", dialog)
        dialog.zscale = QtWidgets.QLineEdit()
        dialog.zscale.setValidator(QtGui.QDoubleValidator())
        dialog.zscale.setText("1.0")        

        d_zshift = QtWidgets.QLabel("Z shift:", dialog)
        dialog.zshift = QtWidgets.QLineEdit()
        dialog.zshift.setValidator(QtGui.QDoubleValidator())
        dialog.zshift.setText("1.0")
        
        if surface is not None:
            dialog.zscale.setText(str(surface.transform_z[0]))
            dialog.zshift.setText(str(surface.transform_z[1]))
        
        grid.addWidget(d_zscale, row+4, 0)
        grid.addWidget(dialog.zscale, row+4, 1)
        grid.addWidget(d_zshift, row+4, 3)
        grid.addWidget(dialog.zshift, row+4, 4)
        
        return row+5
