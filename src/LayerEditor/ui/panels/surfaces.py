"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore
import os
import b_spline
import bspline as bs
import numpy as np

class Surfaces(QtWidgets.QWidget):
    """
    GeoMop Layer editor surfaces panel
    
    pyqtSignals:
        * :py:attr:`showMash() <showMash>`
        * :py:attr:`hideMash() <hideMash>`
        
    All regions function contains history operation without label and
    must be placed after first history operation with label.
    """
    
    showMash = QtCore.pyqtSignal()
    """Signal is sent when mash shoud be show o repaint."""
    
    hideMash = QtCore.pyqtSignal()
    """Signal is sent when mash shoud be hide."""
    
    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Surfaces, self).__init__(parent)
        surfaces = cfg.layers.surfaces
        self.qs = None
        """Help variable of GridSurface type from bspline library. If this variable is None
        , valid approximation is not loaded"""
                
        grid = QtWidgets.QGridLayout(self)
        
        # surface cobobox
        self.surface = QtWidgets.QComboBox()            
        for i in range(0, len(surfaces.surfaces)):            
            label = surfaces[i].name 
            self.surface.addItem( label,  i) 
        self.surface.currentIndexChanged.connect(self._serface_set)
        self.add_surface = QtWidgets.QPushButton("Add Surface")
        self.add_surface.clicked.connect(self._add_surface)            
              
        grid.addWidget(self.surface, 0, 0, 1, 2)
        grid.addWidget(self.add_surface, 0, 2)
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 1, 0, 1, 3)
        
        # frid file
        self.d_grid_file = QtWidgets.QLabel("Grid File:")
        self.grid_file_name = QtWidgets.QLineEdit()
        self.grid_file_button = QtWidgets.QPushButton("...")
        self.grid_file_button.clicked.connect(self._add_grid_file)
        
        grid.addWidget(self.d_grid_file, 2, 0, 1, 2)        
        grid.addWidget(self.grid_file_button , 2, 2)
        grid.addWidget(self.grid_file_name, 3, 0, 1, 3)
        
        # surface name
        self.d_name = QtWidgets.QLabel("Name:")
        self.name = QtWidgets.QLineEdit()
        
        grid.addWidget(self.d_name, 4, 0)        
        grid.addWidget(self.name, 4, 1, 1, 2)
        
        # xz scale        
        self.d_xyscale = QtWidgets.QLabel("XY scale:", self)
        self.xyscale11 = QtWidgets.QLineEdit()
        self.xyscale11.setValidator(QtGui.QDoubleValidator())        
        self.xyscale12 = QtWidgets.QLineEdit()
        self.xyscale12.setValidator(QtGui.QDoubleValidator())        
        self.xyscale21 = QtWidgets.QLineEdit()
        self.xyscale21.setValidator(QtGui.QDoubleValidator())
        self.xyscale22 = QtWidgets.QLineEdit()
        self.xyscale22.setValidator(QtGui.QDoubleValidator())        
        
        self.d_xyshift = QtWidgets.QLabel("XY shift:", self)        
        self.xyshift1 = QtWidgets.QLineEdit()
        self.xyshift1.setValidator(QtGui.QDoubleValidator())
        
        self.xyshift2 = QtWidgets.QLineEdit()
        self.xyshift2.setValidator(QtGui.QDoubleValidator())        
        
        grid.addWidget(self.d_xyscale, 5, 0, 1, 2)
        grid.addWidget(self.d_xyshift, 5, 2)
        grid.addWidget(self.xyscale11, 6, 0)
        grid.addWidget(self.xyscale21, 6, 1)        
        grid.addWidget(self.xyshift1, 6, 2)        
        grid.addWidget(self.xyscale12, 7, 0)
        grid.addWidget(self.xyscale22, 7, 1)
        grid.addWidget(self.xyshift2, 7, 2)
        
        # approximation points
        self.d_approx = QtWidgets.QLabel("Approximation points (u,v):", self)        
        self.u_approx = QtWidgets.QLineEdit()
        self.u_approx.setValidator(QtGui.QIntValidator())
        self.v_approx = QtWidgets.QLineEdit()
        self.v_approx.setValidator(QtGui.QIntValidator())
        
        grid.addWidget(self.d_approx, 8, 0, 1, 3)
        grid.addWidget(self.u_approx, 9, 0)
        grid.addWidget(self.v_approx, 9, 1)
        
        self.delete = QtWidgets.QPushButton("Delete")
        self.delete.clicked.connect(self._delete)
        self.apply = QtWidgets.QPushButton("Apply")
        self.apply.clicked.connect(self._apply)            
              
        grid.addWidget(self.delete, 10, 0)
        grid.addWidget(self.apply, 10, 1, 1, 2)
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 11, 0, 1, 3)

        self.d_depth = QtWidgets.QLabel("Depth:", self)        
        self.depth = QtWidgets.QLineEdit()
        self.depth.setValidator(QtGui.QDoubleValidator())
        grid.addWidget(self.d_depth, 12, 0, 1, 2)
        grid.addWidget(self.depth, 12, 2)

        self.d_error = QtWidgets.QLabel("Approximation error:", self)        
        self.error = QtWidgets.QLineEdit()
        self.error.setValidator(QtGui.QDoubleValidator())
        grid.addWidget(self.d_error, 13, 0, 1, 2)
        grid.addWidget(self.error, 13, 2)   
 
        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 14, 0, 1, 3)
        
        self.setLayout(grid)
        
        self._set_default_approx(None) 
    
    def _apply(self):
        """Save changes to file and compute new depth and error"""
        pass   
       
    def _delete(self):
        """Delete surface if is not used"""
        pass
        
    def _serface_set(self):
        """Surface in combo box was changed"""
        pass
        
    def _add_surface(self):
        """New surface is added"""
        pass
        
    def _add_grid_file(self):
        """Clicked event for _file_button"""
        home = cfg.config.data_dir
        file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose grid file", home,"File (*.*)")
        if file[0]:
            self.grid_file_name.setText(file[0])   
            self._set_default_approx(file[0]) 

    def _set_default_approx(self, file):
        """Set default scales, aprox points and Name"""
        self.xyscale11.setText("1.0")        
        self.xyscale12.setText("0.0")
        self.xyscale21.setText("0.0")
        self.xyscale22.setText("1.0")
        self.xyshift1.setText("0.0")
        self.xyshift2.setText("0.0")
        self.depth.setText("")
        self.error.setText("")        
        
        if file is None or len(file)==0 or file.isspace():
            self._enable_approx(False)
            self.zs = None
        else:
            name = os.path.splitext(file)[0]
            s_i = ""
            i = 2
            while self._name_exist(name+s_i):
                s_i = "_"+str(i)
                i += 1
            name = name+s_i
            self.name.setText(name)  
            if not os.path.exists(file):
                self._enable_approx(False)
                self.zs = None
            else:
                self._enable_approx(True)
                self.gs = bs.GridSurface.load(file)
                self.gs.transform([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], gs)
                # TODO get default params                
            
    def _name_exist(self, name):
        """Test if set surface name exist"""
        surfaces = cfg.layers.surfaces
        for surface in surfaces.surfaces:
            if surface.name==name:
                return True
        return False
            
    def _enable_approx(self, enable):
        """Enable approx controls"""
        # surface name
        self.d_name.setEnabled(enable)
        self.name.setEnabled(enable)
        self.d_xyscale.setEnabled(enable)
        self.xyscale11.setEnabled(enable)
        self.xyscale12.setEnabled(enable)
        self.xyscale21.setEnabled(enable)
        self.xyscale22.setEnabled(enable)
        self.d_xyshift.setEnabled(enable)
        self.xyshift1.setEnabled(enable)
        self.xyshift2.setEnabled(enable)
        self.d_approx.setEnabled(enable)
        self.u_approx.setEnabled(enable)
        self.v_approx.setEnabled(enable)
        self.delete.setEnabled(enable)  
        self.apply.setEnabled(enable) 
        
    def _load_approximation(self):
        """Load approximation from file and refresh error and depth"""
        
    def _save_approximation(self):
        """Save approximation from file and refresh error and depth"""
