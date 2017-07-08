"""
Dialogs for settings text name property or depth
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from .validator_helpers import ValidatorHelpers

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

class SetDepthDlg(QtWidgets.QDialog):

    def __init__(self, value,  parent=None, min=None, max=None):
        super(SetDepthDlg, self).__init__(parent)
        self.setWindowTitle("Set Depth")

        grid = QtWidgets.QGridLayout(self)
        
        d_depth = QtWidgets.QLabel("Set Interface Depth:", self)
        self.depth = QtWidgets.QLineEdit()
        self.validator = QtGui.QDoubleValidator()
        
        if min is not None:
            self.validator.setBottom( min)
        if max is not None:
            self.validator.setTop( max)
        self.validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        
        self.depth.setValidator(self.validator)
        self.depth.setText(str(value))
        
        grid.addWidget(d_depth, 0, 0)
        grid.addWidget(self.depth, 0, 1)

        self._tranform_button = QtWidgets.QPushButton("Set Depth", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, 1, 1)
        self.setLayout(grid)

    def accept(self):
        """
        Accepts the form if depth data fields are valid.
        :return: None
        """
        if ValidatorHelpers.validate_depth(self.depth, self.validator, self):
             super(SetDepthDlg, self).accept()
