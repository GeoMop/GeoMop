"""Dialog for creating new file with optional templates.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QMessageBox, QDialogButtonBox, QPushButton
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
import os

"""
location            -> QLineEdit
name                -> QLineEdit
browse_button       -> QDialogButtonBox
water_flow          -> QGroupBox
darcy               -> QRadioButton
solute_transport    -> QGroupBox
dg                  -> QRadioButton
heat_transfer       -> QCheckBox
"""


class NewFileDialog(QDialog):
    def __init__(self, parent=None, default_directory=''):
        """Initializes the class."""
        super(NewFileDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'new_file_dialog.ui'), self)

        self.location.setText(default_directory)
        self.browse_button.clicked.connect(self._open_file_browser)
        self.button_box.button(QDialogButtonBox.Ok).setText("Create")
        self.button_box.button(QDialogButtonBox.Ok).setIcon(QIcon())
        self.button_box.button(QDialogButtonBox.Cancel).setIcon(QIcon())

    def _open_file_browser(self):
        """Gets location to store new file from user"""
        new_location = QFileDialog.getExistingDirectory(self.parent(), "Select Base Directory",
                                                        self.location.text(), QFileDialog.ShowDirsOnly)
        self.location.setText(QDir.toNativeSeparators(new_location))
        self.location.setFocus()

    def get_directory(self):
        """Returns location specified by user"""
        return os.path.join(self.location.text(), "")

    def get_file_name(self):
        """Returns filename specified by user"""
        name = self.name.text()
        if not name.lower().endswith('.yaml'):
            name += '.yaml'
        return os.path.join(self.location.text(), name)

    def templates(self):
        """Returns a list of yaml template names"""
        templates = ["00_header.yaml"]
        if self.water_flow.isChecked():
            if self.darcy.isChecked():
                templates.append("01_flow_darcy.yaml")
            else:
                templates.append("01_flow_richards.yaml")

        if self.solute_transport.isChecked():
            if self.dg.isChecked():
                templates.append("02_transport_DG.yaml")
            else:
                templates.append("02_transport_FV.yaml")

        if self.heat_transfer.isChecked():
            templates.append("03_heat.yaml")

        return templates

    def done(self, p_int):
        """Check if provided information are correct and end dialog if they are"""
        if p_int == QDialog.Rejected:
            super().done(p_int)
        else:
            if not self.name.text():
                msg = QMessageBox(self)
                msg.setWindowTitle("Empty Name")
                msg.setText("Please specify name of the new file!")
                msg.exec_()

            elif not self.location.text():
                msg = QMessageBox(self)
                msg.setWindowTitle("Empty Base Directory")
                msg.setText("Please specify existing location of the new file!")
                msg.exec_()

            elif not os.path.isdir(self.get_directory()):
                msg = QMessageBox(self)
                msg.setWindowTitle("Wrong Base Directory")
                msg.setText("Please specify existing location of the new file!")
                msg.exec_()

            elif os.path.isfile(self.get_file_name()):
                msg = QMessageBox(self)
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                msg.setWindowTitle("File exists")
                msg.setText("Specified file already exists. Do you wish to override it")
                if msg.exec_() == msg.Ok:
                    super().done(p_int)

            else:
                super().done(p_int)


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    ui = NewFileDialog(default_directory=QDir.homePath())
    sys.exit(ui.exec())
