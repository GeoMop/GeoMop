"""
Dialog for inicialization empty diagram.
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
from leconfig import cfg

class SetDiagramDlg(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(SetDiagramDlg, self).__init__(parent)
        self.setWindowTitle("Set Slice Inicialization Method")

        grid = QtWidgets.QGridLayout(self)
        
        self.grid = QtWidgets.QRadioButton("")
        d_grid_file = QtWidgets.QLabel("Grid File:")
        self.grid_file_name = QtWidgets.QLineEdit()
        self.grid_file_button = QtWidgets.QPushButton("...")
        self.grid_file_button.clicked.connect(self._add_grid_file)
        
        grid.addWidget(self.grid, 0, 0)
        grid.addWidget(d_grid_file, 0, 1)
        grid.addWidget(self.grid_file_name, 0, 2)
        grid.addWidget(self.grid_file_button , 0, 3)        
        
        self.shp = QtWidgets.QRadioButton("")
        d_shp_file = QtWidgets.QLabel("Shape File:")
        self.shp_file_name = QtWidgets.QLineEdit()
        self.shp_file_button = QtWidgets.QPushButton("...")        
        self.shp_file_button.clicked.connect(self._add_shp_file)
        
        grid.addWidget(self.shp, 1, 0)
        grid.addWidget(d_shp_file, 1, 1)
        grid.addWidget(self.shp_file_name, 1, 2)
        grid.addWidget(self.shp_file_button , 1, 3)
        
        self.coordinates = QtWidgets.QRadioButton("")
        self.coordinates.setChecked(True)
        d_coordinates = QtWidgets.QLabel("Coordinates:", self)
        
        d_x = QtWidgets.QLabel("x:", self)
        d_x.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.x = QtWidgets.QLineEdit()
        self.x.setText("0.0")
        self.x.setValidator(QtGui.QDoubleValidator())
        
        d_y = QtWidgets.QLabel("y:", self)
        d_y.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.y = QtWidgets.QLineEdit()
        self.y.setText("0.0")
        self.y.setValidator(QtGui.QDoubleValidator())
        
        d_dx = QtWidgets.QLabel("dx:", self)
        d_dx.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.dx = QtWidgets.QLineEdit()
        self.dx.setText("100.0")
        self.dx.setValidator(QtGui.QDoubleValidator())
        
        d_dy = QtWidgets.QLabel("dy:", self)
        d_dy.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.dy = QtWidgets.QLineEdit()
        self.dy.setText("100.0")
        self.dy.setValidator(QtGui.QDoubleValidator())
        
        grid.addWidget(self.coordinates, 2, 0, 1, 2)
        grid.addWidget(d_coordinates, 2, 1, 1, 2)
        
        grid.addWidget(d_x, 3, 1)
        grid.addWidget(self.x, 3, 2)
        grid.addWidget(d_dx, 3, 3)
        grid.addWidget(self.dx, 3, 4)
        
        grid.addWidget(d_y, 4, 1)
        grid.addWidget(self.y, 4, 2)
        grid.addWidget(d_dy, 4, 3)
        grid.addWidget(self.dy, 4, 4)
        
        self._inicializa_button = QtWidgets.QPushButton("Inicialize New", self)
        self._inicializa_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Open Existing ...", self)
        self._cancel_button.clicked.connect(self.reject)
        
        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._inicializa_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, 5, 3, 1, 2)
        self.setLayout(grid)
        
    def _add_grid_file(self):
        """Clicked event for _file_button"""
        home = cfg.config.data_dir
        file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose grid file", home,"File (*.*)")
        if file[0]:
            self._grid_file_name.setText(file[0])

    def _add_shp_file(self):
        """Clicked event for _file_button"""
        home = cfg.config.data_dir
        file = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose shape file", home,"File (*.shp)")
        if file[0]:
            self._shp_file_name.setText(file[0])
            
    def accept(self):
        """
        Accepts the form if file data fields are valid
        and inicialize dialog
        :return: None
        """
        ret = True
        
        if ret:
            super(SetDiagramDlg, self).accept()
