"""
Dialog for adding fracture to interface.
"""

import PyQt5.QtWidgets as QtWidgets
import gm_base.icon as icon

class AddFractureDlg(QtWidgets.QDialog):

    def __init__(self, le_model, parent=None):
        super(AddFractureDlg, self).__init__(parent)
        self.le_model = le_model
        self.setWindowTitle("Add Fracture")

        grid = QtWidgets.QGridLayout(self)

        d_fracture_name = QtWidgets.QLabel("Fracture Name:", self)
        self.fracture_name = QtWidgets.QLineEdit()
        self.set_default_name()
        self.fracture_name.textChanged.connect(self.frac_name_changed)

        self.image = QtWidgets.QLabel(self)
        self.image.setMinimumWidth(self.fracture_name.sizeHint().height())
        self.image.setPixmap(icon.get_app_icon("sign-check").pixmap(self.fracture_name.sizeHint().height()))
        self.image.setToolTip('Fracture name is unique, everything is fine.')

        grid.addWidget(d_fracture_name, 0, 0)
        grid.addWidget(self.fracture_name, 0, 1)
        grid.addWidget(self.image, 0, 2)

        next_row = 1

        d_fracture_position = QtWidgets.QLabel("Fracture position:", self)
        self.fracture_position = QtWidgets.QComboBox()
        for description in ["Top surface", "Own surface", "Bottom surface"]:
            self.fracture_position.addItem(description)
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

        grid.addWidget(button_box, next_row, 1, 1, 2)
        self.setLayout(grid)

    def frac_name_changed(self, name):
        """ Called when Region Line Edit is changed."""
        if self.le_model.is_layer_name_unique(name):
            self.image.setPixmap(
                icon.get_app_icon("sign-check").pixmap(self.fracture_name.sizeHint().height())
            )
            self.image.setToolTip('Unique name is OK.')
            self._tranform_button.setEnabled(True)
        else:
            self.image.setPixmap(
                icon.get_app_icon("warning").pixmap(self.fracture_name.sizeHint().height())
            )
            self.image.setToolTip('Name is not unique!')
            self._tranform_button.setEnabled(False)

    def set_default_name(self):
        """ Set default name if it seems to be default name. """
        frac_idx = 1
        name = f"Fracture_{frac_idx}"
        while not self.le_model.is_layer_name_unique(name):
            frac_idx += 1
            name = f"Fracture_{frac_idx}"
        self.fracture_name.setText(name)