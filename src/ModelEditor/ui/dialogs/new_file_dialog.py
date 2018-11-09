"""Dialog for creating new file with optional templates.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QToolButton, QLineEdit, QFileDialog, QMessageBox, QGroupBox, QRadioButton,\
                            QCheckBox, QDialogButtonBox
from PyQt5.QtCore import QDir
import os


class NewFileDialog(QDialog):
    def __init__(self, parent=None, default_directory=''):
        """Initializes the class."""
        super(NewFileDialog, self).__init__(parent)
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)),'new_file_dialog.ui'), self)

        self.location.setText(default_directory)
        #self.findChild(QLineEdit, "location").setText(default_directory)
        self.findChild(QToolButton, "browse_button").clicked.connect(self._open_file_browser)
        self.findChild(QDialogButtonBox, "button_box").button(QDialogButtonBox.Ok).setText("Create")

    def _open_file_browser(self):
        """Gets location to store new file from user"""
        location_widget = self.findChild(QLineEdit, "location")
        new_location = QFileDialog.getExistingDirectory(self.parent(), "Select Base Directory",
                                                        location_widget.text(), QFileDialog.ShowDirsOnly)
        location_widget.setText(QDir.toNativeSeparators(new_location))
        location_widget.setFocus()

    def get_directory(self):
        """Returns location specified by user"""
        return os.path.join(self.findChild(QLineEdit, "location").text(), "")

    def get_file_name(self):
        """Returns filename specified by user"""
        name = self.findChild(QLineEdit, "name").text()
        if not name.lower().endswith('.yaml'):
            name += '.yaml'
        return os.path.join(self.findChild(QLineEdit, "location").text(), name)

    def templates(self):
        """Returns a list of yaml template names"""
        templates = ["00_header.yaml"]
        if self.findChild(QGroupBox, "water_flow").isChecked():
            if self.findChild(QRadioButton, "darcy").isChecked():
                templates.append("01_flow_darcy.yaml")
            else:
                templates.append("01_flow_richards.yaml")

        if self.findChild(QGroupBox, "solute_transport").isChecked():
            if self.findChild(QRadioButton, "dg").isChecked():
                templates.append("02_transport_DG.yaml")
            else:
                templates.append("02_transport_FV.yaml")

        if self.findChild(QCheckBox, "heat_transfer").isChecked():
            templates.append("03_heat.yaml")

        return templates

    def done(self, p_int):
        """Check if provided information are correct and end dialog if they are"""
        if p_int == QDialog.Rejected:
            super().done(p_int)
        else:
            location = self.findChild(QLineEdit, "location").text()
            if not self.findChild(QLineEdit, "name").text():
                msg = QMessageBox(self)
                msg.setWindowTitle("Empty Name")
                msg.setText("Please specify name of the new file!")
                msg.exec_()

            elif not location:
                msg = QMessageBox(self)
                msg.setWindowTitle("Empty Base Directory")
                msg.setText("Please specify existing location of the new file!")
                msg.exec_()

            elif not os.path.isdir(location):
                msg = QMessageBox(self)
                msg.setWindowTitle("Wrong Base Directory")
                msg.setText("Please specify existing location of the new file!")
                msg.exec_()

            else:
                super().done(p_int)


if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    ui = NewFileDialog(default_directory=QDir.homePath())
    sys.exit(ui.exec())
