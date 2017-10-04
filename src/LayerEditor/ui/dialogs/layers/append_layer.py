"""
Dialog for appending new layer to the end.
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from .layers_helpers import LayersHelpers

class AppendLayerDlg(QtWidgets.QDialog):

    def __init__(self, parent, min_depth=None ,max_depth=None, prepend=False, add=False):
        super(AppendLayerDlg, self).__init__(parent)
        if add:
            self.setWindowTitle("Add Layer to Shadow Block")
        elif prepend:
            self.setWindowTitle("Add Layer")
        else:
            self.setWindowTitle("Prepend Layer")
        grid = QtWidgets.QGridLayout(self)
        
        d_layer_name = QtWidgets.QLabel("Layer Name:", self)
        self.layer_name = QtWidgets.QLineEdit()
        self.layer_name.setText("New Layer")
        grid.addWidget(d_layer_name, 0, 0)
        grid.addWidget(self.layer_name, 0, 1)
        
        d_surface = QtWidgets.QLabel("Bottom Interface Surface:", self)
        grid.addWidget(d_surface, 1, 0)
        i = LayersHelpers.add_surface_to_grid(self, grid, 2)
        
        self.validator = QtGui.QDoubleValidator()
        if add:
            self.validator.setBottom(min_depth)
            self.validator.setTop( max_depth)
            self.depth.setText(str(max_depth))
        elif prepend:
            self.validator.setTop( max_depth)
            self.depth.setText(str(max_depth-100))
        else:
            self.validator.setBottom( min_depth)
            self.depth.setText(str(min_depth+100))
        self.depth.setValidator(self.validator)
        
        if add:
            self._tranform_button = QtWidgets.QPushButton("Add", self)
        elif prepend:
            self._tranform_button = QtWidgets.QPushButton("Prepend", self)
        else:
            self._tranform_button = QtWidgets.QPushButton("Append", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, i, 3, 1, 3)
        self.setLayout(grid)

    def accept(self):
        """
        Accepts the form if depth data fields are valid.
        :return: None
        """
        if LayersHelpers.validate_depth(self.depth, self.validator, self):
            super(AppendLayerDlg, self).accept()
            
    def fill_surface(self, surface):
        """Fill set surface"""
        return LayersHelpers.fill_surface(self, surface)
