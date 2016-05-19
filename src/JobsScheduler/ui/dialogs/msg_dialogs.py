"""Module contains Message Dialogs.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices


class FilesSavedMessageBox(QtWidgets.QMessageBox):
    """Modified MessageBox to display 'Show in Dir' button."""

    def __init__(self, parent, directory):
        super(FilesSavedMessageBox, self).__init__(parent)
        self.directory = directory
        self.setIcon(QtWidgets.QMessageBox.Information)
        self.setWindowTitle('Files saved')
        self.setText('Files were successfully saved to %s' % directory)
        self.showFilesButton = QtWidgets.QPushButton('Show files in directory')
        self.showFilesButton.clicked.connect(self._showFilesButton_clicked)
        self.addButton(self.showFilesButton, QtWidgets.QMessageBox.AcceptRole)
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.setDefaultButton(QtWidgets.QMessageBox.Ok)

    def _showFilesButton_clicked(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.directory))
