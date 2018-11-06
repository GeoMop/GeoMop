"""Module contains dialogs for search functions - find and replace.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QToolButton, QPlainTextEdit
from PyQt5 import QtGui

class NewFileDialog(QDialog):
    def __init__(self, parent=None, default_path=None):
        """Initializes the class."""
        super(NewFileDialog, self).__init__(parent)
        self.default_path = default_path
        uic.loadUi("../uiDesigns/new_file_dialog.ui", self)
        self.findChild(QToolButton,"browseButton").clicked.connect(self._open_file_browser)

    def _open_file_browser(self):
        location_widget = self.findChild(QPlainTextEdit,"Location")
        new_location = QtWidgets.QFileDialog.getSaveFileName(self, "Choose location...",location_widget.toPlainText())
        location_widget.setPlainText(new_location[0])
        location_widget.moveCursor(QtGui.QTextCursor.End)
        location_widget.setFocus()

if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    NewFileWidget = QtWidgets.QDialog()
    ui = NewFileDialog()
    ui.show()
    sys.exit(app.exec_())