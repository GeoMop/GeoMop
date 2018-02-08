"""
Dialog for appending new layer to the end.
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from .layers_helpers import LayersHelpers

class SplitLayerDlg(QtWidgets.QDialog):

    def __init__(self, min, max, copy_block, parent=None):
        super(SplitLayerDlg, self).__init__(parent)
        self.setWindowTitle("Split Layer")

        grid = QtWidgets.QGridLayout(self)
        
        d_layer_name = QtWidgets.QLabel("Layer Name:", self)
        self.layer_name = QtWidgets.QLineEdit()
        self.layer_name.setToolTip("New Layer name (New layer is in the bottom)")
        self.layer_name.setText("New layer")
        grid.addWidget(d_layer_name, 0, 0)
        grid.addWidget(self.layer_name, 0, 1)
        
        d_split_type = QtWidgets.QLabel("Split Interface Type:", self)
        self.split_type = LayersHelpers.split_type_combo(copy_block)
        
        grid.addWidget(d_split_type, 1, 0)
        grid.addWidget(self.split_type, 1, 1)
        
        d_surface = QtWidgets.QLabel("Split in Surface:", self)
        grid.addWidget(d_surface, 2, 0)
        i = LayersHelpers.add_surface_to_grid(self, grid, 3)
        
        self.validator = QtGui.QDoubleValidator()
        self.validator.setBottom(min)
        self.validator.setTop(max)
        self.elevation.setValidator(self.validator)
        self.elevation.setText(str((min+max)/2))
        
        self._tranform_button = QtWidgets.QPushButton("Split", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, i, 1, 1, 2)
        self.setLayout(grid)

    def accept(self):
        """
        Accepts the form if elevation data fields are valid.
        :return: None
        """
        if LayersHelpers.validate_depth(self.elevation, self.validator, self):
            super(SplitLayerDlg, self).accept()

    def fill_surface(self, interface):
        """Fill set surface"""
        return LayersHelpers.fill_surface(self, interface)
