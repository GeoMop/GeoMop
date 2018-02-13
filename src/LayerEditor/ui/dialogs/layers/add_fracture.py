"""
Dialog for adding fracture to interface.
"""

import PyQt5.QtWidgets as QtWidgets
from leconfig import cfg
import PyQt5.QtGui as QtGui

class AddFractureDlg(QtWidgets.QDialog):

    def __init__(self, fracture_positions, parent=None):
        super(AddFractureDlg, self).__init__(parent)
        self.setWindowTitle("Add Fracture")

        grid = QtWidgets.QGridLayout(self)

        def check_unique(foo):
            unique_name = True
            for _, fracture in cfg.diagram.regions.layers.items():
                if foo == fracture:
                    unique_name = False
            if unique_name:
                self.image.setPixmap(
                    QtGui.QIcon.fromTheme("emblem-default").pixmap(self.fracture_name.sizeHint().height())
                )
                self.image.setToolTip('Fracture name is unique, everything is fine.')
                self._tranform_button.setEnabled(True)
            else:
                self.image.setPixmap(
                    QtGui.QIcon.fromTheme("emblem-important").pixmap(self.fracture_name.sizeHint().height())
                )
                self.image.setToolTip('Fracture name is not unique!')
                self._tranform_button.setEnabled(False)

        d_fracture_name = QtWidgets.QLabel("Fracture Name:", self)
        self.fracture_name = QtWidgets.QLineEdit()
        self.fracture_name.setText("Fracture_" + str(len(cfg.diagram.regions.layers)+1))
        self.fracture_name.textChanged.connect(check_unique)

        self.image = QtWidgets.QLabel(self)
        self.image.setMinimumWidth(self.fracture_name.sizeHint().height())
        self.image.setPixmap(QtGui.QIcon.fromTheme("emblem-default").pixmap(self.fracture_name.sizeHint().height()))
        self.image.setToolTip('Fracture name is unique, everything is fine.')

        grid.addWidget(d_fracture_name, 0, 0)
        grid.addWidget(self.fracture_name, 0, 1)
        grid.addWidget(self.image, 0, 2)



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
