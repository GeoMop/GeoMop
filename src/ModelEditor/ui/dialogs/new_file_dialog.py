"""Module contains dialogs for search functions - find and replace.

.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

class NewFileDialog(QDialog):
    def __init__(self, parent=None):
        """Initializes the class."""
        super(NewFileDialog, self).__init__(parent)
        self = uic.loadUi("../uiDesigns/new_file_dialog.ui",self)





if __name__ == "__main__":
    import sys
    from PyQt5 import QtWidgets
    app = QtWidgets.QApplication(sys.argv)
    NewFileWidget = QtWidgets.QDialog()
    ui = NewFileDialog()
    ui.show()
    sys.exit(app.exec_())