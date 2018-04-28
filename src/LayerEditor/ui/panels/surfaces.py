"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

from LayerEditor.leconfig import cfg

import os
import gm_base.b_spline
import numpy as np
import bspline_approx as ba
from gm_base.geomop_dialogs import GMErrorDialog
import gm_base.icon as icon
from ..data import SurfacesHistory
import copy


class FocusLineEdit(QtWidgets.QLineEdit):
    """
    Focus is not propagated by signal but by QEvent.
    Do not know how to catch FocusIn event for the Surfaces widget
    or any of its childs. For QPushButton we use FocusProxy
    but for LineEdit this unable editing. So we must override the focusInEvent handler.
    """
    def __init__(self, focus_action):
        self._focus_action = focus_action
        super().__init__()

    def focusInEvent(self, event):
        self._focus_action()
        super().focusInEvent(event)


def float_safe(text):
    try:
        return float(text)
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


    show_grid = QtCore.pyqtSignal(bool)
    """Signal is sent when mash shoud be show o repaint.
    
    :param bool force: if force not set, don't call mash if already exist
    """
    
    hide_grid = QtCore.pyqtSignal()
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

        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        grid = QtWidgets.QGridLayout(self)     
        
        # surface cobobox
        self.surface = QtWidgets.QComboBox()
        self.surface.setEditable(True)

        surfaces = cfg.layers.surfaces
        for i in range(0, len(surfaces.surfaces)):
            label = surfaces.surfaces[i].name
            self.surface.addItem( label,  i)

        self.surface.currentIndexChanged.connect(self._surface_set)
        self.surface.activated.connect(self._focus_in)
        self.surface.highlighted.connect(self._focus_in)
        self.add_surface = self.make_button(
            "add", None, 'Add new surface to the assignable list.',
            self._add_surface)
        self.delete = self.make_button(
            "remove", None, 'Remove selected surface from the list.',
            self._delete)

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
        self.grid_file_name = FocusLineEdit(self._focus_in)
        self.grid_file_name.setReadOnly(True)
        self.grid_file_name.setStyleSheet("background-color:WhiteSmoke");
        self.grid_file_button = self.make_button(
            "folder", None, 'Browse local files for the grid file.',
            self._add_grid_file)
        self.grid_file_refresh_button = self.make_button(
            "refresh", None, 'Refresh the working surface.',
            self._refresh_grid_file)

        
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
        self.name = FocusLineEdit(self._focus_in)
        
        grid.addWidget(self.d_name, 7, 0)
        grid.addWidget(self.name, 7, 1, 1, 2)
        
        # xz scale

        self.d_xyscale = QtWidgets.QLabel("XY scale:", self)
        self.d_xyshift = QtWidgets.QLabel("XY shift:", self)

        self.xyscale_mat = [self.make_double_edit() for i in range(6)]

        # Labels in row 8
        grid.addWidget(self.d_xyscale, 8, 0, 1, 2)
        grid.addWidget(self.d_xyshift, 8, 2)
        # Matrix entries in rows 9, 10
        for i in range(2):
            for j in range(3):
                grid.addWidget(self.xyscale_mat[3*i + j], 9+i, j)

        # approximation points
        self.d_approx = QtWidgets.QLabel("Approximation points (u,v):", self)
        self.u_approx = self.make_int_edit()
        self.v_approx = self.make_int_edit()

        grid.addWidget(self.d_approx, 11, 0, 1, 3)
        grid.addWidget(self.u_approx, 12, 0)
        grid.addWidget(self.v_approx, 12, 1)
        
        self.apply = self.make_button(
            None, "Apply", 'Compute approximation and save to the surface list.',
            self._apply)

        grid.addWidget(self.apply, 12,2)
        
        # separator
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


    def make_button(self, icon_name, text, tooltip, method):
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
        button.setFocusProxy(self)
        return button



    def make_double_edit(self):
        edit = FocusLineEdit(self._focus_in)
        #edit.focusIn.connect(self._focus_in)
        edit.textChanged.connect(self._refresh_grid)
        edit.setValidator(QtGui.QDoubleValidator())
        return edit

    def make_int_edit(self):
        edit = FocusLineEdit(self._focus_in)
        edit.textChanged.connect(self._refresh_mash)
        edit.setValidator(QtGui.QIntValidator())
        return edit

    def set_xymat_form(self, values):
        """
        :param values: np array with 2x3 doubles
        """
        for form, val in zip(self.xyscale_mat, values.flat):
            form.setText(str(val))

    # def mousePressEvent(self, event):
    #     super(Surfaces, self).mousePressEvent(event)
    #     self._focus_in()
    
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
            self.hide_grid.emit()
        else:            
            self.show_grid.emit(False)
            
        self.new = new
            
    def get_curr_quad(self):
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
        self.zs.transform(self._get_transform(), None)
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
        self.show_grid.emit(True)
       
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
        self.show_grid.emit(True)

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

        self.show_grid.emit(True)
        self.elevation.setEnabled(False)
        self.error.setEnabled(False)


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
        

    def _focus_in(self):
        """Some controll gain focus"""
        print("Have focus")
        if self.quad is not None:
            self.show_grid.emit(False)
  
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
        self.set_xymat_form(xy_transform)
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
            self.show_grid.emit(True)

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
            self.show_grid.emit(True)
        
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
        mat = [ float_safe(mat_item.text()) for mat_item in self.xyscale_mat]
        return np.array(mat, dtype=float).reshape(2,3)

    def _set_default_approx(self, file):
        """Set default scales, aprox points and Name"""
        self.set_xymat_form(np.array([[1,0,0],[0,1,0]], dtype=float))
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
                self.zs.transform(self._get_transform(), None)
                self.quad = self.zs.quad
                self.show_grid.emit(True)


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
        self.d_xyshift.setEnabled(enable)
        for form in self.xyscale_mat:
            form.setEnabled(enable)
        self.d_approx.setEnabled(enable)
        self.u_approx.setEnabled(enable)
        self.v_approx.setEnabled(enable)
        self.apply.setEnabled(enable)
