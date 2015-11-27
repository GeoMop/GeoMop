"""Module contains dialogs for search functions - find and replace.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import (QDialog, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QCheckBox, QGridLayout, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt, QEvent


class FindReplaceDialog(QDialog):
    """Dialog for finding and replacing text in editor."""

    search = pyqtSignal(str, bool, bool, bool)
    """
    When signal is triggered, a search should be performed.

    :param str search term: text to be looked for
    :param bool is_regex: whether search term is regular expression
    :param bool is_case_sensitive: whether search is case sensitive
    :param bool is_word: whether to look only for entire words
    """

    replace = pyqtSignal(str, str, bool, bool, bool)
    """
    When signal is triggered, currently selected text should be replaced and next search performed.

    :param str search term: text to be looked for
    :param str replacement_text: the replacement text
    :param bool is_regex: whether search term is regular expression
    :param bool is_case_sensitive: whether search is case sensitive
    :param bool is_word: whether to look only for entire words
    """

    replace_all = pyqtSignal(str, str, bool, bool, bool)
    """
    When signal is triggered, all occurrences that match the search term should be replaced.

    :param str search term: text to be looked for
    :param str replacement_text: the replacement text
    :param bool is_regex: whether search term is regular expression
    :param bool is_case_sensitive: whether search is case sensitive
    :param bool is_word: whether to look only for entire words
    """

    def __init__(self, parent, replace_visible=False, defaults=None):
        """Initializes the class.

        :param parent: Qt parent
        :param bool replace_visible: whether replace part of dialog is shown
        :param FindReplaceDialog defaults: previous dialog (to extract default values from)
        """
        super(FindReplaceDialog, self).__init__(parent)

        self._replace_visible = replace_visible

        # find components
        self._find_label = QLabel('Search for: ', self)
        self._find_label.setMinimumSize(85, 20)
        self._find_line_edit = QLineEdit(self)
        self._find_line_edit.textChanged.connect(self.perform_find)
        self._find_line_edit.returnPressed.connect(self.perform_find)
        self._find_line_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self._find_line_edit.setMinimumSize(150, 20)
        self._cs_check_box = QCheckBox('Match Case', self)
        self._cs_check_box.setFocusPolicy(Qt.NoFocus)
        self._re_check_box = QCheckBox('RegEx', self)
        self._re_check_box.setFocusPolicy(Qt.NoFocus)
        self._wo_check_box = QCheckBox('Words', self)
        self._wo_check_box.setFocusPolicy(Qt.NoFocus)
        self._find_button = QPushButton('Find Next', self)
        self._find_button.setFocusPolicy(Qt.NoFocus)
        self._find_button.clicked.connect(self.perform_find)

        # replace components
        self._replace_label = QLabel('Replace with: ')
        self._replace_line_edit = QLineEdit()
        self._replace_line_edit.returnPressed.connect(self._on_replace_button_clicked)
        self._replace_button = QPushButton('Replace')
        self._replace_button.setFocusPolicy(Qt.NoFocus)
        self._replace_button.clicked.connect(self._on_replace_button_clicked)
        self._replace_all_button = QPushButton('Replace All')
        self._replace_all_button.setFocusPolicy(Qt.NoFocus)
        self._replace_all_button.clicked.connect(self._on_replace_all_button_clicked)

        # layout
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self._find_label, 0, 0)
        main_layout.addWidget(self._find_line_edit, 0, 1)
        main_layout.addWidget(self._cs_check_box, 0, 2)
        main_layout.addWidget(self._re_check_box, 0, 3)
        main_layout.addWidget(self._wo_check_box, 0, 4)
        main_layout.addWidget(self._find_button, 0, 5)

        if replace_visible:
            main_layout.addWidget(self._replace_label, 1, 0)
            main_layout.addWidget(self._replace_line_edit, 1, 1)
            replace_button_layout = QHBoxLayout()
            replace_button_layout.addStretch()
            replace_button_layout.addWidget(self._replace_button)
            main_layout.addLayout(replace_button_layout, 1, 2, 1, 3)
            main_layout.addWidget(self._replace_all_button, 1, 5)

        self.setLayout(main_layout)

        # tab order
        if replace_visible:
            self.setTabOrder(self._find_line_edit, self._replace_line_edit)
            self.setTabOrder(self._replace_line_edit, self._find_line_edit)
        else:
            self.setTabOrder(self._find_line_edit, self._find_line_edit)

        # set default values
        if defaults is not None:
            if not self.search_term:
                self._find_line_edit.setText(defaults.search_term)
            self._cs_check_box.setChecked(defaults.is_case_sensitive)
            self._re_check_box.setChecked(defaults.is_regex)
            self._wo_check_box.setChecked(defaults.is_word)

        # qt window settings
        self.setWindowFlags(Qt.Tool | Qt.NoDropShadowWindowHint)
        self.setWindowTitle("Find & Replace")

    def activateWindow(self):
        """Activates the window and sets the focus."""
        super(FindReplaceDialog, self).activateWindow()
        self._find_line_edit.selectAll()
        self._find_line_edit.setFocus()

    def close(self):
        """Clear search text on close."""
        self.search_term = ""
        super(FindReplaceDialog, self).close()

    def reject(self):
        """Clear search term on reject."""
        self.search_term = ""
        super(FindReplaceDialog, self).reject()

    def on_match_found(self):
        """Handle when match is found."""
        self._find_line_edit.setStyleSheet("")

    def on_match_not_found(self):
        """Handle when match is not found."""
        self._find_line_edit.setStyleSheet("background-color: #fdd;")

    @property
    def search_term(self):
        """Term entered into the search field."""
        return self._find_line_edit.text()

    @search_term.setter
    def search_term(self, text):
        """Term entered into the search field."""
        self._find_line_edit.setText(text)

    @property
    def replacement_text(self):
        """Replacement text for matches."""
        return self._replace_line_edit.text()

    @property
    def is_case_sensitive(self):
        """Whether search is case sensitive."""
        return self._cs_check_box.isChecked()

    @property
    def is_regex(self):
        """Whether search term is a regular expression."""
        return self._re_check_box.isChecked()

    @property
    def is_word(self):
        """Whether search term should be matched to entire words only."""
        return self._wo_check_box.isChecked()

    def perform_find(self):
        """Perform a search."""
        self.search.emit(self.search_term, self.is_regex, self.is_case_sensitive, self.is_word)

    def _on_replace_button_clicked(self):
        """Handles replace action."""
        self.replace.emit(self.search_term, self.replacement_text,
                          self.is_regex, self.is_case_sensitive, self.is_word)

    def _on_replace_all_button_clicked(self):
        """Handles replace all action."""
        self.replace_all.emit(self.search_term, self.replacement_text,
                              self.is_regex, self.is_case_sensitive, self.is_word)

    def keyPressEvent(self, event):
        """Handle keypress events.

        :param QKeyEvent event: event with the key press information
        """
        if event.type() != QEvent.KeyPress:
            return

        if event.key() == Qt.Key_F3:
            self.perform_find()
        else:
            super(FindReplaceDialog, self).keyPressEvent(event)
