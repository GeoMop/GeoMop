"""CanvasWidget file"""
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from leconfig import cfg
import PyQt5.QtCore as QtCore

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
        self.xyscale11.setText("1.0")
        self.xyscale12 = QtWidgets.QLineEdit()
        self.xyscale12.setValidator(QtGui.QDoubleValidator())
        self.xyscale12.setText("0.0")
        self.xyscale21 = QtWidgets.QLineEdit()
        self.xyscale21.setValidator(QtGui.QDoubleValidator())
        self.xyscale21.setText("0.0")
        self.xyscale22 = QtWidgets.QLineEdit()
        self.xyscale22.setValidator(QtGui.QDoubleValidator())
        self.xyscale22.setText("1.0")
        
#        if surface is not None:
#            self.xyscale11.setText(str(surface.transform_xy[0][0]))
#            self.xyscale12.setText(str(surface.transform_xy[0][1]))
#            self.xyscale21.setText(str(surface.transform_xy[1][0]))
#            self.xyscale22.setText(str(surface.transform_xy[1][1]))
        
        self.d_xyshift = QtWidgets.QLabel("XY shift:", self)        
        self.xyshift1 = QtWidgets.QLineEdit()
        self.xyshift1.setValidator(QtGui.QDoubleValidator())
        self.xyshift1.setText("0.0")
        self.xyshift2 = QtWidgets.QLineEdit()
        self.xyshift2.setValidator(QtGui.QDoubleValidator())
        self.xyshift2.setText("0.0")
        
#        if surface is not None:
#            self.xyshift1.setText(str(surface.transform_xy[0][2]))
#            self.xyshift2.setText(str(surface.transform_xy[1][2]))        
        
        grid.addWidget(self.d_xyscale, 5, 0, 1, 2)
        grid.addWidget(self.d_xyshift, 5, 2)
        grid.addWidget(self.xyscale11, 6, 0)
        grid.addWidget(self.xyscale21, 6, 1)        
        grid.addWidget(self.xyshift1, 6, 2)        
        grid.addWidget(self.xyscale12, 7, 0)
        grid.addWidget(self.xyscale22, 7, 1)
        grid.addWidget(self.xyshift2, 7, 2)
        
        # aproximation points
        self.d_aprox = QtWidgets.QLabel("Aproximation points (u,v):", self)        
        self.u_aprox = QtWidgets.QLineEdit()
        self.u_aprox.setValidator(QtGui.QIntValidator())
        self.v_aprox = QtWidgets.QLineEdit()
        self.v_aprox.setValidator(QtGui.QIntValidator())
        
        grid.addWidget(self.d_aprox, 8, 0, 1, 3)
        grid.addWidget(self.u_aprox, 9, 0)
        grid.addWidget(self.v_aprox, 9, 1)
        
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
