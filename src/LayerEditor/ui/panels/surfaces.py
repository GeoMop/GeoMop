"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore
import os
import b_spline
import numpy as np
import bspline_approx as ba
from geomop_dialogs import GMErrorDialog

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
        self.zs_id = None
        """Help variable of Z-Surface type from bspline library. If this variable is None
        , valid approximation is not loaded"""
        self.quad = None
        """Display rect for mesh"""
        self.new = False
        """New surface is set"""
        self.last_u = 10
        """Last u"""
        self.last_v = 10
        """Last v"""
                
        grid = QtWidgets.QGridLayout(self)
        
        # surface cobobox
        d_surface = QtWidgets.QLabel("Surface:")
        self.surface = QtWidgets.QComboBox()            
        for i in range(0, len(surfaces.surfaces)):            
            label = surfaces.surfaces[i].name 
            self.surface.addItem( label,  i) 
        self.surface.currentIndexChanged.connect(self._surface_set)
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
        self.xyscale11.textChanged.connect(self._refresh_grid)
        self.xyscale11.setValidator(QtGui.QDoubleValidator())        
        self.xyscale12 = QtWidgets.QLineEdit()
        self.xyscale12.textChanged.connect(self._refresh_grid)
        self.xyscale12.setValidator(QtGui.QDoubleValidator())        
        self.xyscale21 = QtWidgets.QLineEdit()
        self.xyscale21.textChanged.connect(self._refresh_grid)
        self.xyscale21.setValidator(QtGui.QDoubleValidator())
        self.xyscale22 = QtWidgets.QLineEdit()
        self.xyscale22.textChanged.connect(self._refresh_grid)
        self.xyscale22.setValidator(QtGui.QDoubleValidator())        
        
        self.d_xyshift = QtWidgets.QLabel("XY shift:", self)        
        self.xyshift1 = QtWidgets.QLineEdit()
        self.xyshift1.textChanged.connect(self._refresh_grid)
        self.xyshift1.setValidator(QtGui.QDoubleValidator())
        
        self.xyshift2 = QtWidgets.QLineEdit()
        self.xyshift2.textChanged.connect(self._refresh_grid)
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
        self.u_approx.textChanged.connect(self._refresh_mash)
        self.u_approx.setValidator(QtGui.QIntValidator())
        self.v_approx = QtWidgets.QLineEdit()
        self.v_approx.textChanged.connect(self._refresh_mash)
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
        
        self.d_origin_x = QtWidgets.QLabel("Origin x:", self)        
        self.origin_x = QtWidgets.QLineEdit()
        self.origin_x.setReadOnly(True)
        self.d_origin_y = QtWidgets.QLabel("Origin y:", self)        
        self.origin_y = QtWidgets.QLineEdit()
        self.origin_y.setReadOnly(True)
        
        grid.addWidget(self.d_origin_x, 17, 0)
        grid.addWidget(self.origin_x, 17, 1, 1, 2) 
        grid.addWidget(self.d_origin_y, 18, 0)
        grid.addWidget(self.origin_y, 18, 1, 1, 2) 
        
        self.d_message = QtWidgets.QLabel("", self)
        self.d_message.setVisible(False)
        grid.addWidget(self.d_message, 19, 0, 1, 3)
 
        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 20, 0, 1, 3)
        
        self.setLayout(grid)
        
        if len(surfaces.surfaces)>0:
            self.surface.setCurrentIndex(0)            
        else:
            self._set_new_edit(True)             
            
    def _set_new_edit(self, new):
        """Set or unset new surface editing"""
        if self.new==new:
            return
        self.delete.setEnabled(not new)
        self.add_surface.setEnabled(not new)
        if new:
            self.zs = None
            self.zs_id = -1
            self.quad = None
            self.grid_file_name.setText("")
            self._set_default_approx(None)            
            self.apply.setText("Add Surface")            
            self.grid_file_refresh_button.setEnabled(False)
            self.surface.setCurrentIndex(-1)
        else:            
            self.apply.setText("Apply")            
        self.new = new
            
    def get_curr_mash(self):
        """Return quad, u, v for mash constraction"""
        u, v = self.get_uv()
        return self.quad, u, v        
            
    def get_surface_id(self):
        return self.surface.currentIndex()
            
    def reload_surfaces(self, id):
        """Reload all surfaces after file loading"""
        surfaces = cfg.layers.surfaces
        self.surface.clear()
        for i in range(0, len(surfaces.surfaces)):            
            label = surfaces.surfaces[i].name 
            self.surface.addItem( label,  i)
        if id is None or len(surfaces.surfaces)>=id:
            if len(surfaces.surfaces)>0:
                self._set_new_edit(False)
            else:
                self._set_new_edit(True)
        else:
            self._set_new_edit(False)
    
    def _apply(self):
        """Save changes to file and compute new depth and error"""
        # TODO: chatch and highlite duplicit item error 
        surfaces = cfg.layers.surfaces
        
        file = self.grid_file_name.text()
        
        self.zs.transform(np.array(self._get_transform(), dtype=float), None)
        self.quad = self.zs.quad.tolist()
        self.origin_x.setText(str(self.quad[1][0]))
        self.origin_y.setText(str(self.quad[1][1]))
        center = self.zs.center()
        self.depth.setText(str(center[2]))
        
        if self.new:
            surfaces.add(self.zs, file, 
                self.name.text(), self._get_transform(), self.quad) 
            self.zs_id = len(surfaces.surfaces)-1
            self.surface.addItem( self.name.text(), len(surfaces.surfaces)-1) 
            self.surface.setCurrentIndex(len(surfaces.surfaces)-1)
            self._set_new_edit(False)           
        else:
            surface = surfaces.surfaces[self.surface.currentData()]
            surface.grid_file = self.grid_file_name.text()
            if surface.name!=self.name.text():
                surface.name = self.name.text()    
                self.surface.setItemText(self.surface.currentIndex(), surface.name)
            surface.xy_transform = self._get_transform()
            surface.quad = self.quad
        self.refreshArrea.emit()
       
    def _delete(self):
        """Delete surface if is not used"""
        id = self.surface.currentIndex()
        if id == -1:
            return 
        if not cfg.layers.delete_surface(id):
            error = "Surface is used" 
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog(error)
            return
        self.reload_surfaces(id)
        
    def _refresh_grid(self, new_str):
        """Grid parameters is changet"""
        if self.zs is None:
            return
        self.zs.reset_transform()
        self.zs.transform(np.array(self._get_transform(), dtype=float), None)
        self.quad = self.zs.quad.tolist()
        self.origin_x.setText(str(self.quad[1][0]))
        self.origin_y.setText(str(self.quad[1][1]))
        center = self.zs.center()
        self.depth.setText(str(center[2]))
        self.showMash.emit()
        
    def get_uv(self):
        """Check and return uv"""
        # TODO: highlite error 
        try:
            u = int(self.u_approx.text())
            if u<10:
                u = 10
        except:
            u = 10
        try:
            v = int(self.v_approx.text())
            if v<10:
                v = 10
        except:
            v = 10
        return u, v
        
    def _refresh_mash(self, new_str):
        """Mash parameters is changet"""
        if self.zs is None:
            return
        u, v = self.get_uv()
        if u!=self.last_u or v!=self.last_v:
            self.last_u = u
            self.last_v = v
        else:
            return
        file = self.grid_file_name.text()
        approx = ba.SurfaceApprox.approx_from_file(file) 
        self.zs = approx.compute_approximation(nuv=np.array([u, v], dtype=int))
        self.zs.transform(np.array(self._get_transform(), dtype=float), None)
        self.quad = self.zs.quad.tolist()
        self.origin_x.setText(str(self.quad[1][0]))
        self.origin_y.setText(str(self.quad[1][1]))
        center = self.zs.center()
        self.depth.setText(str(center[2]))
        self.showMash.emit()
        
    def _surface_set(self):
        """Surface in combo box was changed"""
        id = self.surface.currentIndex()
        if id == -1:
            return        
        if self.zs_id==id:
            return
        self._set_new_edit(False)
        surfaces = cfg.layers.surfaces.surfaces        
        file = surfaces[id].grid_file
        self.grid_file_name.setText(file)
        self.name.setText(surfaces[id].name) 
        self.xyscale11.setText(str(surfaces[id].xy_transform[0][0]))        
        self.xyscale12.setText(str(surfaces[id].xy_transform[0][1]))
        self.xyscale21.setText(str(surfaces[id].xy_transform[1][0]))
        self.xyscale22.setText(str(surfaces[id].xy_transform[1][1]))
        self.xyshift1.setText(str(surfaces[id].xy_transform[0][2]))
        self.xyshift2.setText(str(surfaces[id].xy_transform[1][2]))
        u = surfaces[id].approximation.u_basis.n_intervals
        v = surfaces[id].approximation.v_basis.n_intervals
        self.u_approx.setText(str(u))
        self.v_approx.setText(str(v))
        self.last_u = u
        self.last_v = v  
        self.depth.setText("")
        self.error.setText("")
        self.origin_x.setText("")
        self.origin_y.setText("")
        self.d_message.setText("")
        self.d_message.setVisible(False)
        
        if not os.path.exists(file):
            self.grid_file_refresh_button.setEnabled(False)
            self._enable_approx(False)
            self.quad = surfaces[id].quad
            self.zs = surfaces[id].approximation
            self.zs_id = id
            self.d_message.setText("Set grid file not found.")
            self.d_message.setVisible(True)
        else:
            self.grid_file_refresh_button.setEnabled(True)
            self._enable_approx(True)
            approx = ba.SurfaceApprox.approx_from_file(file) 
            zs = approx.compute_approximation(nuv=np.array([u, v], dtype=int))
            quad = approx.transformed_quad(np.array(self._get_transform(), dtype=float)).tolist()
            self.quad = surfaces[id].quad            
            if not self.cmp_quad(quad, surfaces[id].quad):
                self.zs = surfaces[id].approximation
                self.zs_id = id
                self.d_message.setText("Set grid file get different approximation.")                
                self.d_message.setVisible(True)
            else:
                self.zs = zs
                self.zs_id = id
                if approx.error is not None:
                    self.error.setText(str(approx.error))                
                center = self.zs.center()
                self.depth.setText(str(center[2]))            
            # TODO: check focus
            self.showMash.emit()
        self.origin_x.setText(str(self.quad[1][0]))
        self.origin_y.setText(str(self.quad[1][1]))
            
    def cmp_quad(self, q1, q2):
        """Compare two quad"""
        for i in range(0, 2):
            for j in range(0, 2):
                p = q1[i][j]/q2[i][j]
                if p<0.999999999 or i>1.000000001:
                    return False
        return True
    
    def _add_surface(self):
        """New surface is added"""
        self._set_new_edit(True)       
        
    def _refresh_grid_file(self):
        """Reload grid file"""        
        file = self.name.text() 
        if os.path.exists(file):
            self._enable_approx(True)
            approx = ba.SurfaceApprox.approx_from_file(file)                
            self.zs = approx.compute_approximation()
            self.zs_id = self.surface.currentIndex()
            if approx.error is not None:
                self.error.setText(str(approx.error) )
            center = self.zs.center()
            self.depth.setText(str(center[2]))
            self.quad = approx.transformed_quad(np.array(self._get_transform(), dtype=float)).tolist()
            self.origin_x.setText(str(self.quad[1][0]))
            self.origin_y.setText(str(self.quad[1][1]))
            self.showMash.emit()
        
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
        self.origin_x.setText("")
        self.origin_y.setText("")
        self.d_message.setText("")
        self.d_message.setVisible(False)
        self.last_u = 10
        self.last_v = 10
        self.u_approx.setText("10")
        self.v_approx.setText("10")        
        
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
                self.grid_file_refresh_button.setEnabled(False)
                self._enable_approx(False)
                self.zs = None
            else:
                self.grid_file_refresh_button.setEnabled(True)
                self._enable_approx(True)
                approx = ba.SurfaceApprox.approx_from_file(file)                
                nuv = approx.compute_default_nuv()
                self.u_approx.setText(str(nuv[0]))
                self.v_approx.setText(str(nuv[1]))   
                self.last_u = nuv[0]
                self.last_v = nuv[1]            
                self.zs = approx.compute_approximation()                
                if approx.error is not None:
                    self.error.setText(str(approx.error) )
                center = self.zs.center()
                self.depth.setText(str(center[2]))
                self.quad = approx.transformed_quad(np.array(self._get_transform(), dtype=float)).tolist()
                self.origin_x.setText(str(self.quad[1][0]))
                self.origin_y.setText(str(self.quad[1][1]))
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
        self.apply.setEnabled(enable) 
