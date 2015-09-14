"""
Module contains dialogs for search functions - find and replace.
"""

# pylint: disable=invalid-name

__author__ = 'Tomas Krizek'

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

        self.find_label = None
        self.find_line_edit = None
        self.cs_check_box = None
        self.re_check_box = None
        self.wo_check_box = None
        self.find_button = None
        self.close_button = None

        self.init_components()
        self.init_layout()

    def init_components(self):
        """Initializes the user interface components."""
        self.find_label = QLabel('Search for: ', self)
        self.find_line_edit = QLineEdit(self)
        self.cs_check_box = QCheckBox('Match case', self)
        self.re_check_box = QCheckBox('Regular expression', self)
        self.wo_check_box = QCheckBox('Match entire word only', self)
        self.find_button = QPushButton('Find', self)
        self.find_button.setDefault(True)
        self.find_button.clicked.connect(self.accept)
        self.close_button = QPushButton('Close', self)
        self.close_button.clicked.connect(self.close)

    def init_layout(self):
        """Initializes the layout of widget."""
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.find_label)
        search_layout.addWidget(self.find_line_edit)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.find_button)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.cs_check_box)
        main_layout.addWidget(self.re_check_box)
        main_layout.addWidget(self.wo_check_box)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setFixedSize(FindDialog.WIDTH, FindDialog.HEIGHT)

    def accept(self):
        """Handles a find confirmation."""
        search_term = self.find_line_edit.text()
        is_case_sensitive = self.cs_check_box.isChecked()
        is_regex = self.re_check_box.isChecked()
        is_word = self.wo_check_box.isChecked()
        self.findRequested.emit(search_term, is_regex, is_case_sensitive, is_word)

    def activateWindow(self):
        """Activates the window and sets the focus."""
        super(FindDialog, self).activateWindow()
        self.find_line_edit.selectAll()
        self.find_line_edit.setFocus()


class ReplaceDialog(FindDialog):
    """Dialog for text replacement."""

    WIDTH = 350
    """width of the dialog"""

    HEIGHT = 180
    """height of the dialog"""

    replace_request = pyqtSignal(str, str, bool, bool, bool)
    """
    Signal is triggered when the replace button is clicked.
    Parameters: search term (str), replacement text (str), is regular expression (bool),
                is case sensitive (bool), is entire word (bool)
    When signal is triggered, current selection should be replaced with the replacement text.
    """

    replace_all_request = pyqtSignal(str, str, bool, bool, bool)
    """
    Signal is triggered when the replace all button is clicked.
    Parameters: search term (str), replace text (str), is regular expression (bool),
                is case sensitive (bool), is entire word (bool)
    When signal is triggered, current selection should be replaced with the replacement text
    as well as all other matches, as long as there are some.
    """

    def __init__(self, parent, title='Replace'):
        """Initializes the class."""
        self.replace_label = None
        self.replace_line_edit = None
        self.replace_button = None
        self.replace_all_button = None

        super(ReplaceDialog, self).__init__(parent, title)

    def init_components(self):
        """Initializes the components."""
        super(ReplaceDialog, self).init_components()
        self.replace_label = QLabel('Replace with: ')
        self.replace_line_edit = QLineEdit()
        self.replace_button = QPushButton('Replace')
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button = QPushButton('Replace All')
        self.replace_all_button.clicked.connect(self.replace_all)

    def init_layout(self):
        """Initializes the layout."""
        replace_layout = QGridLayout()
        replace_layout.addWidget(self.find_label, 0, 0)
        replace_layout.addWidget(self.find_line_edit, 0, 1)
        replace_layout.addWidget(self.replace_label, 1, 0)
        replace_layout.addWidget(self.replace_line_edit, 1, 1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        button_layout.addWidget(self.replace_all_button)
        button_layout.addWidget(self.replace_button)
        button_layout.addWidget(self.find_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(replace_layout)
        main_layout.addWidget(self.cs_check_box)
        main_layout.addWidget(self.re_check_box)
        main_layout.addWidget(self.wo_check_box)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.setFixedSize(ReplaceDialog.WIDTH, ReplaceDialog.HEIGHT)

    def replace(self):
        """Handles replace action."""
        search_term = self.find_line_edit.text()
        replacement_text = self.replace_line_edit.text()
        is_case_sensitive = self.cs_check_box.isChecked()
        is_regex = self.re_check_box.isChecked()
        is_word = self.wo_check_box.isChecked()
        self.replace_request.emit(search_term, replacement_text, is_regex,
                                  is_case_sensitive, is_word)

    def replace_all(self):
        """Handles replace all action."""
        search_term = self.find_line_edit.text()
        replacement_text = self.replace_line_edit.text()
        is_case_sensitive = self.cs_check_box.isChecked()
        is_regex = self.re_check_box.isChecked()
        is_word = self.wo_check_box.isChecked()
        self.replace_all_request.emit(search_term, replacement_text, is_regex,
                                      is_case_sensitive, is_word)


if __name__ == '__main__':
    def main():
        """"Launches widget."""
        import sys
        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        dialog = ReplaceDialog(None)
        dialog.show()
        sys.exit(app.exec_())
    main()
