"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore
import os
import b_spline
import numpy as np
import bspline_approx as ba

class Surfaces(QtWidgets.QWidget):
    """
    GeoMop Layer editor surfaces panel
    
    pyqtSignals:
        * :py:attr:`showMash() <showMash>`
        * :py:attr:`hideMash() <hideMash>`
        * :py:attr:`refreshArrea() <refreshArrea>`
        
    All regions function contains history operation without label and
    must be placed after first history operation with label.
    """
    
    showMash = QtCore.pyqtSignal()
    """Signal is sent when mash shoud be show o repaint."""
    
    hideMash = QtCore.pyqtSignal()
    """Signal is sent when mash shoud be hide."""
    
    refreshArrea = QtCore.pyqtSignal()
    """Signal is sent when arrea shoud be refreshed."""    
    
    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Surfaces, self).__init__(parent)
        surfaces = cfg.layers.surfaces
        self.zs = None
        """Help variable of Z-Surface type from bspline library. If this variable is None
        , valid approximation is not loaded"""
        self.quad = None
        """Display rect for mesh"""
        self.new = False
        """New surface is set"""
                
        grid = QtWidgets.QGridLayout(self)
        
        # surface cobobox
        d_surface = QtWidgets.QLabel("Surface:")
        self.surface = QtWidgets.QComboBox()            
        for i in range(0, len(surfaces.surfaces)):            
            label = surfaces[i].name 
            self.surface.addItem( label,  i) 
        self.surface.currentIndexChanged.connect(self._serface_set)
        self.add_surface = QtWidgets.QPushButton("Add Surface")
        self.add_surface.clicked.connect(self._add_surface)  
        self.delete = QtWidgets.QPushButton("Delete Surface")
        self.delete.clicked.connect(self._delete)        

        grid.addWidget(d_surface, 0, 0)
        grid.addWidget(self.surface, 0, 1, 1, 2)
        grid.addWidget(self.delete, 1, 2)
        grid.addWidget(self.add_surface, 1, 0)
        
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 2, 0, 1, 3)
        
        # grid file
        self.d_grid_file = QtWidgets.QLabel("Grid File:")
        self.grid_file_name = QtWidgets.QLineEdit()
        self.grid_file_name.setReadOnly(True)
        self.grid_file_button = QtWidgets.QPushButton("...")
        self.grid_file_button.clicked.connect(self._add_grid_file)
        self.grid_file_refresh_button = QtWidgets.QPushButton("Refresh")
        self.grid_file_refresh_button.clicked.connect(self._refresh_grid_file)
        
        grid.addWidget(self.d_grid_file, 3, 0, 1, 2)        
        grid.addWidget(self.grid_file_button , 3, 2)
        grid.addWidget(self.grid_file_name, 4, 0, 1, 3)
        grid.addWidget(self.grid_file_refresh_button , 5, 2)
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 6, 0, 1, 3)
        
        # surface name
        self.d_name = QtWidgets.QLabel("Name:")
        self.name = QtWidgets.QLineEdit()
        
        grid.addWidget(self.d_name, 7, 0)        
        grid.addWidget(self.name, 7, 1, 1, 2)
        
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
        
        grid.addWidget(self.d_xyscale, 8, 0, 1, 2)
        grid.addWidget(self.d_xyshift, 8, 2)
        grid.addWidget(self.xyscale11, 9, 0)
        grid.addWidget(self.xyscale21, 9, 1)        
        grid.addWidget(self.xyshift1, 9, 2)        
        grid.addWidget(self.xyscale12, 10, 0)
        grid.addWidget(self.xyscale22, 10, 1)
        grid.addWidget(self.xyshift2, 10, 2)
        
        # approximation points
        self.d_approx = QtWidgets.QLabel("Approximation points (u,v):", self)        
        self.u_approx = QtWidgets.QLineEdit()
        self.u_approx.setValidator(QtGui.QIntValidator())
        self.v_approx = QtWidgets.QLineEdit()
        self.v_approx.setValidator(QtGui.QIntValidator())
        
        grid.addWidget(self.d_approx, 11, 0, 1, 3)
        grid.addWidget(self.u_approx, 12, 0)
        grid.addWidget(self.v_approx, 12, 1)        
        
        self.apply = QtWidgets.QPushButton("Apply")
        self.apply.clicked.connect(self._apply)            
        
        grid.addWidget(self.apply, 13, 1, 1, 2)
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 14, 0, 1, 3)

        self.d_depth = QtWidgets.QLabel("Depth:", self)        
        self.depth = QtWidgets.QLineEdit()
        self.depth.setReadOnly(True)
        grid.addWidget(self.d_depth, 15, 0)
        grid.addWidget(self.depth, 15, 1, 1, 2)

        self.d_error = QtWidgets.QLabel("Error:", self)        
        self.error = QtWidgets.QLineEdit()
        self.error.setReadOnly(True)
        
        grid.addWidget(self.d_error, 16, 0)
        grid.addWidget(self.error, 16, 1, 1, 2) 
      
        self.d_message = QtWidgets.QLabel("", self)
        self.d_message.setVisible(False)
        grid.addWidget(self.d_message, 17, 0, 1, 3)
 
        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 18, 0, 1, 3)
        
        self.setLayout(grid)
        
        if len(surfaces.surfaces)>0:
            self.surface.setCurrentIndex(0)
        else:
            self.new = True
            self._set_default_approx(None) 
    
    def _apply(self):
        """Save changes to file and compute new depth and error"""
        surfaces = cfg.layers.surfaces
        
        self.zs.reset_transform()
        self.zs.transform(np.array(self._get_transform(), dtype=float), None)
        self.quad = self.zs.quad.tolist()
        center = self.zs.center()
        self.depth.setText(str(center[2]))
        
        if self.new:
            surfaces.add(self.zs, self.grid_file_name.text(), 
                self.name.text(), self._get_transform(), self.quad)           
            self.surface.addItem( self.name.text(), len(surfaces.surfaces)-1) 
            self.surface.setCurrentIndex(len(surfaces.surfaces)-1)
            self.new = False
        else:
            surface = surfaces.surfaces[self.surface.currentData()]
            surface.grid_file = self.grid_file_name.text()
            surface.name = self.name.text()    
            surface.xy_transform = self._get_transform()
            surface.quad = self.quad
        
        self.showMash.emit()
        self.refreshArrea.emit()
       
    def _delete(self):
        """Delete surface if is not used"""
        pass
        
    def _serface_set(self):
        """Surface in combo box was changed"""
        pass
        
    def _add_surface(self):
        """New surface is added"""
        self._set_default_approx(None) 
        self.surface.setCurrentIndex(-1)
        
    def _refresh_grid_file(self):
        """Reload grid file"""
        pass
        
    def _add_grid_file(self):
        """Clicked event for _file_button"""
        home = cfg.config.data_dir
        file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose grid file", home,"File (*.*)")
        if file[0]:
            self.grid_file_name.setText(file[0])   
            self._set_default_approx(file[0]) 
            
    def _get_transform(self):
        """Return xy transformation from controls"""
        return ((float(self.xyscale11.text()), 
                float(self.xyscale12.text()),float(self.xyshift1.text())), 
                (float(self.xyscale21.text()), float(self.xyscale22.text()),  
                float(self.xyshift2.text())))

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
            name = os.path.basename(name)
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
                approx = ba.SurfaceApprox.approx_from_file(file)                
                nuv = approx.compute_default_nuv()
                self.u_approx.setText(str(nuv[0]))
                self.v_approx.setText(str(nuv[1]))                
                self.zs = approx.compute_approximation()
                if approx.error is not None:
                    self.error.setText(str(approx.error) )
                center = self.zs.center()
                self.depth.setText(str(center[2]))
                self.quad = approx.transformed_quad(np.array(self._get_transform(), dtype=float)).tolist()
                self.showMash.emit()
            
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
