"""
Module contains dialogs for search functions - find and replace.
"""

__author__ = 'Tomas Krizek'

# pylint: disable=no-member,invalid-name

from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton,
                             QLineEdit, QCheckBox, QGridLayout)
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


class ReplaceDialog(FindDialog):
    """Dialog for text replacement."""

    WIDTH = 350
    """width of the dialog"""

    HEIGHT = 180
    """height of the dialog"""

    replaceRequested = pyqtSignal(str, str, bool, bool, bool)
    """
    Signal is triggered when the replace button is clicked.
    Parameters: search term (str), replacement text (str), is regular expression (bool),
                is case sensitive (bool), is entire word (bool)
    When signal is triggered, current selection should be replaced with the replacement text.
    """

    replaceAllRequested = pyqtSignal(str, str, bool, bool, bool)
    """
    Signal is triggered when the replace all button is clicked.
    Parameters: search term (str), replace text (str), is regular expression (bool),
                is case sensitive (bool), is entire word (bool)
    When signal is triggered, current selection should be replaced with the replacement text
    as well as all other matches, as long as there are some.
    """

    def __init__(self, parent, title='Replace'):
        """Initializes the class."""
        self.replaceLabel = None
        self.replaceLineEdit = None
        self.replaceButton = None
        self.replaceAllButton = None

        super(ReplaceDialog, self).__init__(parent, title)

    def initComponents(self):
        """Initializes the components."""
        super(ReplaceDialog, self).initComponents()
        self.replaceLabel = QLabel('Replace with: ')
        self.replaceLineEdit = QLineEdit()
        self.replaceButton = QPushButton('Replace')
        self.replaceButton.clicked.connect(self.replace)
        self.replaceAllButton = QPushButton('Replace All')
        self.replaceAllButton.clicked.connect(self.replaceAll)

    def initLayout(self):
        """Initializes the layout."""
        replaceLayout = QGridLayout()
        replaceLayout.addWidget(self.findLabel, 0, 0)
        replaceLayout.addWidget(self.findLineEdit, 0, 1)
        replaceLayout.addWidget(self.replaceLabel, 1, 0)
        replaceLayout.addWidget(self.replaceLineEdit, 1, 1)

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.closeButton)
        buttonLayout.addWidget(self.replaceAllButton)
        buttonLayout.addWidget(self.replaceButton)
        buttonLayout.addWidget(self.findButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(replaceLayout)
        mainLayout.addWidget(self.csCheckBox)
        mainLayout.addWidget(self.reCheckBox)
        mainLayout.addWidget(self.woCheckBox)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setFixedSize(ReplaceDialog.WIDTH, ReplaceDialog.HEIGHT)

    def replace(self):
        """Handles replace action."""
        search_term = self.findLineEdit.text()
        replacement_text = self.replaceLineEdit.text()
        is_case_sensitive = self.csCheckBox.isChecked()
        is_regex = self.reCheckBox.isChecked()
        is_word = self.woCheckBox.isChecked()
        self.replaceRequested.emit(search_term, replacement_text, is_regex,
                                   is_case_sensitive, is_word)

    def replaceAll(self):
        """Handles reaplceAll action."""
        search_term = self.findLineEdit.text()
        replacement_text = self.replaceLineEdit.text()
        is_case_sensitive = self.csCheckBox.isChecked()
        is_regex = self.reCheckBox.isChecked()
        is_word = self.woCheckBox.isChecked()
        self.replaceAllRequested.emit(search_term, replacement_text, is_regex,
                                      is_case_sensitive, is_word)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = ReplaceDialog(None)
    dialog.show()
    sys.exit(app.exec_())
