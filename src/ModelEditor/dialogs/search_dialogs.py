"""
Module contains dialogs for search functions - find and replace.
"""

__author__ = 'Tomas Krizek'

# pylint: disable=no-member,invalid-name

from PyQt5.QtWidgets import (QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                             QLineEdit, QCheckBox, QSizePolicy)


class FindDialog(QDialog):
    """Dialog for editor searching."""

    def __init__(self, parent=None, title='Find'):
        """Initializes the class."""
        super(FindDialog, self).__init__(parent)
        self.setWindowTitle(title)

        self.findLabel = QLabel('Search for: ')
        self.findLineEdit = QLineEdit()
        self.csCheckBox = QCheckBox('Match case')
        self.reCheckBox = QCheckBox('Regular expression')
        self.findButton = QPushButton('Find')
        self.closeButton = QPushButton('Close')
        self.closeButton.clicked.connect(self.reject)
        self.buttonLayout = None
        self.searchLayout = None

        self.initSearchLayout()
        self.initButtonLayout()
        self.initLayout()

    def initUi(self):
        """Initializes the dialog user interface."""
        layout = QVBoxLayout()

    def initLayout(self):
        """Initializes the layout of widget."""
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.searchLayout)
        mainLayout.addWidget(self.csCheckBox)
        mainLayout.addWidget(self.reCheckBox)
        mainLayout.addLayout(self.buttonLayout)
        self.setLayout(mainLayout)
        self.setFixedSize(350, 150)

    def initSearchLayout(self):
        """Initializes the search layout."""
        self.searchLayout = QHBoxLayout()
        self.searchLayout.addWidget(self.findLabel)
        self.searchLayout.addWidget(self.findLineEdit)

    def initButtonLayout(self):
        """Initializaes the button layout."""
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch()
        self.buttonLayout.addWidget(self.closeButton)
        self.buttonLayout.addWidget(self.findButton)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = FindDialog()
    dialog.show()
    sys.exit(app.exec_())
