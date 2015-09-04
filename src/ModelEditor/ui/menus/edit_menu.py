"""
Module contains an edit menu widget.
"""

__author__ = 'Tomas Krizek'

# pylint: disable=no-member,invalid-name

from PyQt5.QtWidgets import QMenu, QAction
import helpers.keyboard_shortcuts as shortcuts
from dialogs import FindDialog


class EditMenu(QMenu):
    """Menu with editing actions."""

    def __init__(self, parent, editor, title='&Edit'):
        """Initializes the class."""
        super(EditMenu, self).__init__(parent)

        self._editor = editor
        self.aboutToShow.connect(self._check_action_availability)

        self.undo_action = None
        self.redo_action = None
        self.cut_action = None
        self.copy_action = None
        self.paste_action = None
        self.delete_action = None
        self.select_all_action = None
        self.indent_action = None
        self.unindent_action = None
        self.comment_action = None

        self.initActions()
        self.initMenu()

        self.setTitle(title)

    def initActions(self):
        """Initializes the available actions."""
        self.undo_action = QAction('&Undo', self)
        self.undo_action.setShortcut(shortcuts.SCINTILLA['UNDO'].key_sequence)
        self.undo_action.setStatusTip('Undo document changes')
        self.undo_action.triggered.connect(self._editor.undo)

        self.redo_action = QAction('&Redo', self)
        self.redo_action.setShortcut(shortcuts.SCINTILLA['REDO'].key_sequence)
        self.redo_action.setStatusTip('Redo document changes')
        self.redo_action.triggered.connect(self._editor.redo)

        self.cut_action = QAction('Cu&t', self)
        self.cut_action.setShortcut(shortcuts.SCINTILLA['CUT'].key_sequence)
        self.cut_action.setStatusTip('Cut to clipboard')
        self.cut_action.triggered.connect(self._editor.cut)

        self.copy_action = QAction('&Copy', self)
        self.copy_action.setShortcut(shortcuts.SCINTILLA['COPY'].key_sequence)
        self.copy_action.setStatusTip('Copy to clipboard')
        self.copy_action.triggered.connect(self._editor.copy)

        self.paste_action = QAction('&Paste', self)
        self.paste_action.setShortcut(shortcuts.SCINTILLA['PASTE'].key_sequence)
        self.paste_action.setStatusTip('Paste from clipboard')
        self.paste_action.triggered.connect(self._editor.paste)

        self.delete_action = QAction('&Delete', self)
        self.delete_action.setShortcut(shortcuts.SCINTILLA['DELETE'].key_sequence)
        self.delete_action.setStatusTip('Delete selected text')
        self.delete_action.triggered.connect(self._editor.delete)

        self.select_all_action = QAction('Select &All', self)
        self.select_all_action.setShortcut(shortcuts.SCINTILLA['SELECT_ALL'].key_sequence)
        self.select_all_action.setStatusTip('Select entire text')
        self.select_all_action.triggered.connect(self._editor.selectAll)

        self.indent_action = QAction('Indent Block', self)
        self.indent_action.setShortcut(shortcuts.SCINTILLA['INDENT'].key_sequence)
        self.indent_action.setStatusTip('Indents the selected lines')
        self.indent_action.triggered.connect(self._editor.indent)

        self.unindent_action = QAction('Unindent Block', self)
        self.unindent_action.setShortcut(shortcuts.SCINTILLA['UNINDENT'].key_sequence)
        self.unindent_action.setStatusTip('Unindents the selected lines')
        self.unindent_action.triggered.connect(self._editor.unindent)

        self.comment_action = QAction('Toggle Comment', self)
        self.comment_action.setShortcut(shortcuts.SCINTILLA['COMMENT'].key_sequence)
        self.comment_action.setStatusTip('Toggles Comment for the selected lines')
        self.comment_action.triggered.connect(self._editor.comment)

    def initMenu(self):
        """Initializes the menu user interface."""
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addSeparator()
        self.addAction(self.cut_action)
        self.addAction(self.copy_action)
        self.addAction(self.paste_action)
        self.addAction(self.delete_action)
        self.addSeparator()
        self.addAction(self.select_all_action)
        self.addSeparator()
        self.addAction(self.indent_action)
        self.addAction(self.unindent_action)
        self.addAction(self.comment_action)

    def _check_action_availability(self):
        """Enable or disable available actions."""
        self.undo_action.setEnabled(self._editor.isUndoAvailable())
        self.redo_action.setEnabled(self._editor.isRedoAvailable())
        self.cut_action.setEnabled(self._editor.hasSelectedText())
        self.copy_action.setEnabled(self._editor.hasSelectedText())
        self.delete_action.setEnabled(self._editor.hasSelectedText())


class MainEditMenu(EditMenu):
    """
    Represents the main windows edit menu.
    Contains some extra features compared to `EditMenu`.
    """

    def __init__(self, parent, editor, title='&Edit'):
        """Initializes the class."""
        self.parent = parent
        self._editor = editor
        self.findAction = None
        self.findDialog = None
        super(MainEditMenu, self).__init__(parent, editor, title)

    def initActions(self):
        """Initializes the actions."""
        super(MainEditMenu, self).initActions()

        self.find_action = QAction('&Find', self)
        self.find_action.setShortcut(shortcuts.SCINTILLA['FIND'].key_sequence)
        self.find_action.setStatusTip('Searches the document')
        self.find_action.triggered.connect(self.on_find_action)

    def initMenu(self):
        """Initializes the menu user interface."""
        super(MainEditMenu, self).initMenu()
        self.addSeparator()
        self.addAction(self.find_action)

    def on_find_action(self):
        """Handles the find action."""
        if not self.findDialog or not self.findDialog.isVisible():
            self.findDialog = FindDialog(self.parent)
            self.findDialog.findRequested.connect(self._editor.findRequested)

            # move the dialog to top right position of editor
            top_right_editor = self._editor.mapToGlobal(self._editor.geometry().topRight())
            pos_x = top_right_editor.x() - FindDialog.WIDTH - 1
            pos_y = top_right_editor.y() + 1
            self.findDialog.move(pos_x, pos_y)

            self.findDialog.show()

        self.findDialog.activateWindow()
