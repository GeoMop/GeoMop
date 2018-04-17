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
from ui.data import SurfacesHistory
import copy

class FocusEdit(QtWidgets.QLineEdit):
    """LineEdit width focus in event
    
    pyqtSignals:         
        * :py:attr:`focusIn() <focusIn>`
    """
    
    focusIn = QtCore.pyqtSignal()
    """Signal is sent when mash shoud be hide."""
    
    def focusInEvent(self, event):
        """Standart focus event"""
        super(FocusEdit, self).focusInEvent(event)
        self.focusIn.emit()
        
    def getFloat(self):
        """Return float in text field"""
        try:
            return float(self.text())
        except:
            return 0
    
    

class Surfaces(QtWidgets.QWidget):
    """
    GeoMop Layer editor surfaces panel
    
    pyqtSignals:
        * :py:attr:`showMash() <showMash>`
        * :py:attr:`hideMash() <hideMash>`
        * :py:attr:`refreshArea() <refreshArea>`
        
    All regions function contains history operation without label and
    must be placed after first history operation with label.
    """
    
    showMash = QtCore.pyqtSignal(bool)
    """Signal is sent when mash shoud be show o repaint.
    
    :param bool force: if force not set, don't call mash if already exist
    """
    
    hideMash = QtCore.pyqtSignal()
    """Signal is sent when mash shoud be hide."""
    
    refreshArea = QtCore.pyqtSignal()
    """Signal is sent when arrea shoud be refreshed."""    
    
    def __init__(self, parent=None):
        """
        Inicialize window

        Args:
            parent (QWidget): parent window ( empty is None)
        """
        super(Surfaces, self).__init__(parent)

        self.zs = None
        """ Instance of bs.Z_Surface, result of approximation. """
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
        self._history = SurfacesHistory(cfg.history)
        """History class"""
        self.approx=None;
        """Auxiliary object for optimalization"""
                
        grid = QtWidgets.QGridLayout(self)     
        
        # surface cobobox
        self.surface = QtWidgets.QComboBox()

        surfaces = cfg.layers.surfaces
        for i in range(0, len(surfaces.surfaces)):            
            label = surfaces.surfaces[i].name 
            self.surface.addItem( label,  i)

        self.surface.currentIndexChanged.connect(self._surface_set)
        self.surface.activated.connect(self._focus_in)
        self.surface.highlighted.connect(self._focus_in)
        self.add_surface = QtWidgets.QPushButton()
        self.add_surface.setIcon(QtGui.QIcon("../common/icon/24x24/add.png"))
        self.add_surface.setToolTip('Add new surface to the assignable list.')
        self.add_surface.clicked.connect(self._add_surface)
        self.add_surface.pressed.connect(self._focus_in)
        self.delete = QtWidgets.QPushButton()
        self.delete.setIcon(QtGui.QIcon("../common/icon/24x24/remove.png"))
        self.delete.setToolTip('Remove selected surface from the list.')
        self.delete.clicked.connect(self._delete)
        self.delete.pressed.connect(self._focus_in)

        d_surface = QtWidgets.QLabel("Surface:")
        grid.addWidget(d_surface, 0, 0)
        grid.addWidget(self.surface, 0, 1, 1, 2)
        grid.addWidget(self.add_surface, 1, 1)
        grid.addWidget(self.delete, 1, 2)
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 2, 0, 1, 3)
        
        # grid file
        self.d_grid_file = QtWidgets.QLabel("Grid File:")
        self.grid_file_name = FocusEdit()
        self.grid_file_name.setReadOnly(True)
        self.grid_file_name.setStyleSheet("background-color:WhiteSmoke");
        self.grid_file_name.focusIn.connect(self._focus_in)
        self.grid_file_button = QtWidgets.QPushButton()
        self.grid_file_button.setIcon(QtGui.QIcon("../common/icon/24x24/folder.png"))
        self.grid_file_button.setToolTip('Browse local files for the grid file.')
        self.grid_file_button.clicked.connect(self._add_grid_file)
        self.grid_file_button.pressed.connect(self._focus_in)
        self.grid_file_refresh_button = QtWidgets.QPushButton()
        self.grid_file_refresh_button.setIcon(QtGui.QIcon("../common/icon/24x24/refresh.png"))
        self.grid_file_refresh_button.setToolTip('Refresh the working surface.')
        self.grid_file_refresh_button.clicked.connect(self._refresh_grid_file)
        self.grid_file_refresh_button.pressed.connect(self._focus_in)
        
        grid.addWidget(self.d_grid_file, 3, 0, 1, 2)
        grid.addWidget(self.grid_file_button, 3, 1)
        grid.addWidget(self.grid_file_refresh_button, 3, 2)
        grid.addWidget(self.grid_file_name, 4, 0, 1, 3)

        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 6, 0, 1, 3)
        
        # surface name
        self.d_name = QtWidgets.QLabel("Name:")
        self.name = FocusEdit()
        self.name.focusIn.connect(self._focus_in)
        
        grid.addWidget(self.d_name, 7, 0)        
        grid.addWidget(self.name, 7, 1, 1, 2)
        
        # xz scale        
        self.d_xyscale = QtWidgets.QLabel("XY scale:", self)
        self.xyscale11 = FocusEdit()
        self.xyscale11.textChanged.connect(self._refresh_grid)
        self.xyscale11.focusIn.connect(self._focus_in)
        self.xyscale11.setValidator(QtGui.QDoubleValidator())        
        self.xyscale12 = FocusEdit()
        self.xyscale12.textChanged.connect(self._refresh_grid)
        self.xyscale12.focusIn.connect(self._focus_in)
        self.xyscale12.setValidator(QtGui.QDoubleValidator())        
        self.xyscale21 = FocusEdit()
        self.xyscale21.textChanged.connect(self._refresh_grid)
        self.xyscale21.focusIn.connect(self._focus_in)
        self.xyscale21.setValidator(QtGui.QDoubleValidator())
        self.xyscale22 = FocusEdit()
        self.xyscale22.textChanged.connect(self._refresh_grid)
        self.xyscale22.focusIn.connect(self._focus_in)
        self.xyscale22.setValidator(QtGui.QDoubleValidator())        
        
        self.d_xyshift = QtWidgets.QLabel("XY shift:", self)        
        self.xyshift1 = FocusEdit()
        self.xyshift1.textChanged.connect(self._refresh_grid)
        self.xyshift1.focusIn.connect(self._focus_in)
        self.xyshift1.setValidator(QtGui.QDoubleValidator())
        
        self.xyshift2 = FocusEdit()
        self.xyshift2.textChanged.connect(self._refresh_grid)
        self.xyshift2.focusIn.connect(self._focus_in)
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
        self.u_approx = FocusEdit()
        self.u_approx.textChanged.connect(self._refresh_mash)
        self.u_approx.focusIn.connect(self._focus_in)
        self.u_approx.setValidator(QtGui.QIntValidator())
        self.v_approx = FocusEdit()
        self.v_approx.textChanged.connect(self._refresh_mash)
        self.v_approx.focusIn.connect(self._focus_in)
        self.v_approx.setValidator(QtGui.QIntValidator())
        
        grid.addWidget(self.d_approx, 11, 0, 1, 3)
        grid.addWidget(self.u_approx, 12, 0)
        grid.addWidget(self.v_approx, 12, 1)        
        
        self.apply = QtWidgets.QPushButton("Apply")
        self.apply.clicked.connect(self._apply) 
        self.apply.pressed.connect(self._focus_in)
        
        grid.addWidget(self.apply, 12,2)
        
        # sepparator
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        grid.addWidget(line, 13, 0, 1, 3)
        
        
        inner_grid = QtWidgets.QGridLayout()

        self.d_elevation = QtWidgets.QLabel("Elevation:", self)
        self.elevation = QtWidgets.QLineEdit()
        self.elevation.setReadOnly(True)
        self.elevation.setStyleSheet("background-color:WhiteSmoke");
        self.elevation.setEnabled(False)
        inner_grid.addWidget(self.d_elevation, 0, 0)
        inner_grid.addWidget(self.elevation, 0, 1)

        self.d_error = QtWidgets.QLabel("Error:", self)        
        self.error = QtWidgets.QLineEdit()
        self.error.setReadOnly(True)
        self.error.setStyleSheet("background-color:WhiteSmoke");
        self.error.setEnabled(False)
        
        inner_grid.addWidget(self.d_error, 0, 2)
        inner_grid.addWidget(self.error, 0, 3)
        
        grid.addLayout(inner_grid, 14, 0, 1, 3)
        
        self.d_message = QtWidgets.QLabel("", self)
        self.d_message.setVisible(False)
        grid.addWidget(self.d_message, 15, 0, 1, 3)
 
        sp1 =  QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        grid.addItem(sp1, 16, 0, 1, 3)
        
        self.setLayout(grid)

        if len(surfaces.surfaces)>0:
            self.surface.setCurrentIndex(0)            
        else:
            self._set_new_edit(True)

    def mousePressEvent(self, event):
        super(Surfaces, self).mousePressEvent(event)
        self._focus_in()
    
    def focusInEvent(self, event):
        """Standart focus event"""
        super(Surfaces, self).focusInEvent(event)
        self._focus_in()
            
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
            self.grid_file_refresh_button.setEnabled(False)
            self.surface.setCurrentIndex(-1)
            self.hideMash.emit()            
        else:            
            self.showMash.emit(False)
            
        self.new = new
            
    def get_curr_mash(self):
        """Return quad, u, v for mash constraction"""
        u, v = self.get_uv()
        return self.quad, u, v        
            
    def get_surface_id(self):
        return self.surface.currentIndex()
            
    def reload_surfaces(self, id=None, set_history=False):
        """Reload all surfaces after file loading"""
        if set_history:
            self._history = SurfacesHistory(cfg.history)
        if id is None:
            id = self.surface.currentIndex()
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
        """Save changes to file and compute new elevation and error"""
        # TODO: chatch and highlite duplicit item error 
        surfaces = cfg.layers.surfaces
        
        file = self.grid_file_name.text()
        u, v = self.get_uv()
        
        self.zs = self.approx.compute_approximation(nuv=np.array([u, v], dtype=int))
        self.zs.transform(np.array(self._get_transform(), dtype=float), None)
        self.quad = self.zs.quad.tolist()
        
        if self.new:
            surfaces.add(self.zs, file, self.name.text())
            self.zs_id = len(surfaces.surfaces)-1
            self.surface.addItem( self.name.text(), len(surfaces.surfaces)-1) 
            self._history.delete_surface(len(surfaces.surfaces)-1)
            self.surface.setCurrentIndex(len(surfaces.surfaces)-1)
            self._set_new_edit(False)           
        else:
            id = self.surface.currentData()

            # Set Surface
            surface = copy.copy(surfaces.surfaces[id])
            surface.approximation = self.zs
            surface.grid_file = self.grid_file_name.text()
            if surface.name!=self.name.text():
                surface.name = self.name.text()    
                self.surface.setItemText(self.surface.currentIndex(), surface.name)
            self._history.change_surface(surfaces, id)
            surfaces.surfaces[id] = surface
        if self.approx.error is not None:
            self.error.setText(str(self.approx.error))                
        else:
            self.error.setText("")
        center = self.zs.center()
        self.elevation.setText(str(center[2]))
        self.elevation.setEnabled(True)
        self.error.setEnabled(True)
        self.elevation.home(False)
        self.error.home(False) 
        self.showMash.emit(True)
       
    def _delete(self):
        """Delete surface if is not used"""
        id = self.surface.currentIndex()
        if id == -1:
            return 
        del_surface = cfg.layers.surfaces.surfaces[id]
        if not cfg.layers.delete_surface(id):
            error = "Surface is used" 
            err_dialog = GMErrorDialog(self)
            err_dialog.open_error_dialog(error)
            return
        self._history.insert_surface(del_surface, id)    
        self.reload_surfaces(id)
        
    def _refresh_grid(self, new_str):
        """Transform parameters arechanged."""
        if self.zs is None:
            return
        t_mat = np.array(self._get_transform(), dtype=float)
        # Check for inverted and singular transform.
        # Physicaly reasonable scaling is about 9 orders of magnitude, 2D determinant should be greater
        # then 1e-18 and we make some reserve.
        if np.linalg.det(t_mat[0:2,0:2]) < 1e-20:
            # TODO: mark actual field invalid
            return
        self.zs.transform(t_mat, None)
        self.quad = self.zs.quad.tolist()        
        self.showMash.emit(True)
        
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
        """Mesh parameters nu, nv have changed."""
        if self.zs is None:
            return
        u, v = self.get_uv()
        if u!=self.last_u or v!=self.last_v:
            self.last_u = u
            self.last_v = v
        else:
            return

        self.showMash.emit(True)
        self.elevation.setEnabled(False)
        self.error.setEnabled(False)

    def _focus_in(self):
        """Some controll gain focus"""
        if self.quad is not None:
            self.showMash.emit(False)
  
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

        approx = surfaces[id].approximation
        xy_transform = approx.get_transform()[0]
        self.xyscale11.setText(str(xy_transform[0][0]))
        self.xyscale12.setText(str(xy_transform[0][1]))
        self.xyscale21.setText(str(xy_transform[1][0]))
        self.xyscale22.setText(str(xy_transform[1][1]))
        self.xyshift1.setText(str(xy_transform[0][2]))
        self.xyshift2.setText(str(xy_transform[1][2]))
        u = approx.u_basis.n_intervals
        v = approx.v_basis.n_intervals
        self.u_approx.setText(str(u))
        self.v_approx.setText(str(v))
        self.last_u = u
        self.last_v = v  
        self.elevation.setText("")
        self.error.setText("")
        self.elevation.setEnabled(False)
        self.error.setEnabled(False)          
        self.d_message.setText("")
        self.d_message.setVisible(False)
        
        if os.path.exists(file):
            try:
                self.approx = ba.SurfaceApprox.approx_from_file(file)  
            except:
                self.d_message.setText("Invalid file.")
                self.approx = None
        
        if self.approx is None:
            self.grid_file_refresh_button.setEnabled(False)
            self._enable_approx(False)
            self.zs = surfaces[id].approximation
            self.quad = self.zs.quad
            assert np.all(np.array(self.quad) == np.array(self.zs.quad))
            self.zs_id = id
            self.d_message.setText("Set grid file not found.")
            self.d_message.setVisible(True)
        else:
            self.grid_file_refresh_button.setEnabled(True)
            self._enable_approx(True)

            # This approx is recomputed to check that file doesn't change (so the quad match).
            zs = self.approx.compute_approximation(nuv=np.array([u, v], dtype=int))
            zs.transform(np.array(self._get_transform(), dtype=float), None)

            self.quad = surfaces[id].approximation.quad
            if not np.allclose(np.array(zs.quad), np.array(self.quad)) :
                self.zs = surfaces[id].approximation
                self.zs_id = id
                self.d_message.setText("Set grid file get different approximation.")                
                self.d_message.setVisible(True)
            else:
                self.zs = zs
                self.zs_id = id
                if self.approx.error is not None:
                    self.error.setText(str(self.approx.error))                
                center = self.zs.center()
                self.elevation.setText(str(center[2]))
                self.elevation.setEnabled(True)
                self.error.setEnabled(True)
                self.elevation.home(False)
                self.error.home(False) 
            # TODO: check focus
            self.showMash.emit(True)

    def _add_surface(self):
        """New surface is added"""
        self._set_new_edit(True)       
        
    def _refresh_grid_file(self):
        """Reload grid file"""        
        file = self.name.text() 
        
        if os.path.exists(file):
            try:
                self.approx = ba.SurfaceApprox.approx_from_file(file)  
            except:
                self.d_message.setText("Invalid file.")
                self.approx = None
        
        if self.approx is not None:
            self._enable_approx(True)
            self.zs = self.approx.compute_approximation()
            self.zs_id = self.surface.currentIndex()
            if self.approx.error is not None:
                self.error.setText(str(self.approx.error) )
            center = self.zs.center()
            self.elevation.setText(str(center[2]))
            self.elevation.setEnabled(True)
            self.error.setEnabled(True) 
            self.elevation.home(False)
            self.error.home(False)          
            self.zs.transform(np.array(self._get_transform(), dtype=float), None)
            self.quad = self.zs.quad
            self.showMash.emit(True)
        
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
        return ((self.xyscale11.getFloat(), 
                self.xyscale12.getFloat(),self.xyshift1.getFloat()), 
                (self.xyscale21.getFloat(), self.xyscale22.getFloat(),  
                self.xyshift2.getFloat()))

    def _set_default_approx(self, file):
        """Set default scales, aprox points and Name"""
        self.xyscale11.setText("1.0")        
        self.xyscale12.setText("0.0")
        self.xyscale21.setText("0.0")
        self.xyscale22.setText("1.0")
        self.xyshift1.setText("0.0")
        self.xyshift2.setText("0.0")
        self.elevation.setText("")
        self.error.setText("") 
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

            # TODO have general machanism to this in common. Given a list of names
            # and given a name prefix return a first unique name.
            # usage: get_unique_name(name, [surf.name for surf in surfaces.surfaces])
            while self._name_exist(name+s_i):
                s_i = "_"+str(i)
                i += 1
            name = name+s_i
            self.name.setText(name)  
            self.aprox = None
            if os.path.exists(file):
                try:
                    self.approx = ba.SurfaceApprox.approx_from_file(file)  
                except:
                    self.d_message.setText("Invalid file.")
                    self.approx = None            
            if self.approx is None:
                self.grid_file_refresh_button.setEnabled(False)
                self._enable_approx(False)
                self.zs = None
            else:
                self.grid_file_refresh_button.setEnabled(True)
                self._enable_approx(True)                              
                nuv = self.approx.compute_default_nuv()
                self.u_approx.setText(str(nuv[0]))
                self.v_approx.setText(str(nuv[1]))   
                self.last_u = nuv[0]
                self.last_v = nuv[1]            

                self.zs = self.approx.compute_approximation()
                if self.approx.error is not None:
                    self.error.setText(str(self.approx.error) )
                center = self.zs.center()
                self.elevation.setText(str(center[2]))
                self.elevation.setEnabled(True)
                self.error.setEnabled(True)
                self.elevation.home(False)
                self.error.home(False)           
                self.zs.transform(np.array(self._get_transform(), dtype=float), None)
                self.quad = self.zs.quad                
                self.showMash.emit(True)


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
