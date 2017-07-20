"""
Dialog for appending new layer to the end.
"""

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui
from .layers_helpers import LayersHelpers

class AppendLayerDlg(QtWidgets.QDialog):

    def __init__(self, min_depth, parent, prepend=False):
        super(AppendLayerDlg, self).__init__(parent)
        if prepend:
            self.setWindowTitle("Append Layer")
        else:
            self.setWindowTitle("Prepend Layer")
        grid = QtWidgets.QGridLayout(self)
        
        d_layer_name = QtWidgets.QLabel("Layer Name:", self)
        self.layer_name = QtWidgets.QLineEdit()
        self.layer_name.setText("New Layer")
        grid.addWidget(d_layer_name, 0, 0)
        grid.addWidget(self.layer_name, 0, 1)
        
        d_depth = QtWidgets.QLabel("Bottom Interface Depth:", self)
        self.depth = QtWidgets.QLineEdit()
        self.validator = QtGui.QDoubleValidator()
        if prepend:
            self.validator.setTop( min_depth)
             self.depth.setText(str(min_depth-100))
        else:
            self.validator.setBottom( min_depth)
             self.depth.setText(str(min_depth+100))
        self.depth.setValidator(self.validator)
       
        
        grid.addWidget(d_depth, 1, 0)
        grid.addWidget(self.depth, 1, 1)

        if prepend:
            self._tranform_button = QtWidgets.QPushButton("Prepend", self)
        else:
            self._tranform_button = QtWidgets.QPushButton("Append", self)
        self._tranform_button.clicked.connect(self.accept)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self.reject)

        button_box = QtWidgets.QDialogButtonBox()
        button_box.addButton(self._tranform_button, QtWidgets.QDialogButtonBox.AcceptRole)
        button_box.addButton(self._cancel_button, QtWidgets.QDialogButtonBox.RejectRole)

        grid.addWidget(button_box, 2, 1)
        self.setLayout(grid)

    def accept(self):
        """
        Accepts the form if depth data fields are valid.
        :return: None
        """
        if LayersHelpers.validate_depth(self.depth, self.validator, self):
            super(AppendLayerDlg, self).accept()
