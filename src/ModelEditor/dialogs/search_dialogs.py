"""
Module contains dialogs for search functions - find and replace.
"""

__author__ = 'Tomas Krizek'

# pylint: disable=no-member,invalid-name

from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                             QLineEdit, QCheckBox)
from PyQt5.QtCore import pyqtSignal


class FindDialog(QDialog):
    """Dialog for editor searching."""

    findRequested = pyqtSignal(str, bool, bool, bool)
    """
    Signal is triggered when the find button is clicked.
    Parameters: search term (str), is regular expression (bool), is case sensitive (bool),
                is entire word (bool)
    """

    WIDTH = 350
    """width of the dialog"""

    HEIGHT = 150
    """height of the dialog"""

    def __init__(self, parent, title='Find'):
        """Initializes the class."""
        super(FindDialog, self).__init__(parent)
        self.setWindowTitle(title)

        self.findLabel = None
        self.findLineEdit = None
        self.csCheckBox = None
        self.reCheckBox = None
        self.woCheckBox = None
        self.findButton = None
        self.closeButton = None

        self.initComponents()
        self.initLayout()

    def initComponents(self):
        """Initializes the user interface components."""
        self.findLabel = QLabel('Search for: ')
        self.findLineEdit = QLineEdit()
        self.csCheckBox = QCheckBox('Match case')
        self.reCheckBox = QCheckBox('Regular expression')
        self.woCheckBox = QCheckBox('Match entire word only')
        self.findButton = QPushButton('Find')
        self.findButton.setDefault(True)
        self.findButton.clicked.connect(self.accept)
        self.closeButton = QPushButton('Close')
        self.closeButton.clicked.connect(self.close)

    def initLayout(self):
        """Initializes the layout of widget."""
        searchLayout = QHBoxLayout()
        searchLayout.addWidget(self.findLabel)
        searchLayout.addWidget(self.findLineEdit)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.findButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(searchLayout)
        mainLayout.addWidget(self.csCheckBox)
        mainLayout.addWidget(self.reCheckBox)
        mainLayout.addWidget(self.woCheckBox)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setFixedSize(FindDialog.WIDTH, FindDialog.HEIGHT)

    def accept(self):
        """Handles a find confirmation."""
        search_term = self.findLineEdit.text()
        is_case_sensitive = self.csCheckBox.isChecked()
        is_regex = self.reCheckBox.isChecked()
        is_word = self.woCheckBox.isChecked()
        self.findRequested.emit(search_term, is_regex, is_case_sensitive, is_word)

    def activateWindow(self):
        """Activates the window and sets the focus."""
        super(FindDialog, self).activateWindow()
        self.findLineEdit.selectAll()
        self.findLineEdit.setFocus()


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = FindDialog(None)
    dialog.show()
    sys.exit(app.exec_())
