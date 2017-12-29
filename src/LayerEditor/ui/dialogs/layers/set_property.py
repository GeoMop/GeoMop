"""
Dialogs for settings text name property or depth
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from .layers_helpers import LayersHelpers

class SetNameDlg(QtWidgets.QDialog):

    def __init__(self,  value, category, parent=None):
        super(SetNameDlg, self).__init__(parent)
        self.setWindowTitle("Set {0} Name".format(category))

        grid = QtWidgets.QGridLayout(self)
        
        d_name = QtWidgets.QLabel("Layer {0} Name:".format(category), self)
        self.name = QtWidgets.QLineEdit()
        self.name.setText(value)
        grid.addWidget(d_name, 0, 0)
        grid.addWidget(self.name, 0, 1)

        self._tranform_button = QtWidgets.QPushButton("Set Name", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, 1, 1)
        self.setLayout(grid)

class SetSurfaceDlg(QtWidgets.QDialog):

    def __init__(self, interface,  parent=None, min=None, max=None):
        super(SetSurfaceDlg, self).__init__(parent)
        self.setWindowTitle("Set Surface")

        grid = QtWidgets.QGridLayout(self)
        
        d_surface = QtWidgets.QLabel("Set Interface Surface:", self)
        grid.addWidget(d_surface, 0, 0)
        i = LayersHelpers.add_surface_to_grid(self, grid, 1, interface)
        
        self.validator = QtGui.QDoubleValidator()
        
        if min is not None:
            self.validator.setBottom( min)
        if max is not None:
            self.validator.setTop( max)
        self.validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        
        self.depth.setValidator(self.validator)
        
        self._tranform_button = QtWidgets.QPushButton("Set Surface", self)
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
        Accepts the form if depth data fields are valid.
        :return: None
        """
        if LayersHelpers.validate_depth(self.depth, self.validator, self):
             super(SetSurfaceDlg, self).accept()
             
    def fill_surface(self, interface):
        """Fill set surface"""
        return LayersHelpers.fill_surface(self, interface)
