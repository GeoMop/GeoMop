"""
Dialog for inicialization empty diagram.
"""

import PyQt5.QtWidgets as QtWidgets
from leconfig import cfg

class SetDiagramDlg(QtWidgets.QDialog):

    def __init__(self, fracture_positions, parent=None):
        super(SetDiagramDlg, self).__init__(parent)
        self.setWindowTitle("Set Slice Inicialization Method")

        grid = QtWidgets.QGridLayout(self)
        
        self.grid = QRadioButton("")
        d_file = QtWidgets.QLabel("Grid File:")
        self.file_name = QtWidgets.QLineEdit()
        self.file_button = QtWidgets.QPushButton("...")
        self.file_button.clicked.connect(_add_file)
        
        
        self.shp = QRadioButtonx("")
        self.coordinates = QRadioButton("")

        
        d_fracture_name = QtWidgets.QLabel("Fracture Name:", self)
        self.fracture_name = QtWidgets.QLineEdit()
        self.fracture_name.setText("New Fracture")
        grid.addWidget(d_fracture_name, 0, 0)
        grid.addWidget(self.fracture_name, 0, 1)
        
        next_row = 1 
        self.fracture_position = None
        if  fracture_positions is not None:
            d_fracture_position = QtWidgets.QLabel("Fracture position:", self)
            self.fracture_position = QtWidgets.QComboBox()
            for description, value in fracture_positions.items():
                self.fracture_position.addItem(description,  value)
            self.fracture_position.setCurrentIndex(0)
            grid.addWidget(d_fracture_position, 1, 0)
            grid.addWidget(self.fracture_position, 1, 1)
            next_row = 2

        self._tranform_button = QtWidgets.QPushButton("Add", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, next_row, 1)
        self.setLayout(grid)
        
    def _add_file(self):
        """Clicked event for _file_button"""
        home = cfg.config.data_dir
        file = QtWidgets.QFileDialog.getOpenFileName(
            dialog, "Choose grif file", home,"File (*.*)")
        if file[0]:
            self._file_name.setText(file[0])
