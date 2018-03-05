"""Module contains an edit menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QMenu, QAction

from ModelEditor.meconfig import cfg


class EditMenu(QMenu):
    """Menu with editing actions."""

    def __init__(self, parent, editor, line=None, title='&Edit'):
        """
        Initializes the class.
        
        :param int line: Prefered line. If menu action is emit by mouse click, 
            line is clicked line
        """
        super(EditMenu, self).__init__(parent)

        self._editor = editor
        self.line = line
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

        self.init_actions()
        self.init_menu()

        self.setTitle(title)

    def init_actions(self):
        """Initializes the available actions."""
        self.undo_action = QAction('&Undo', self)
        self.undo_action.setShortcut(cfg.get_shortcut('undo').key_sequence)
        self.undo_action.setStatusTip('Undo document changes')
        self.undo_action.triggered.connect(self._editor.undo)

        self.redo_action = QAction('&Redo', self)
        self.redo_action.setShortcut(cfg.get_shortcut('redo').key_sequence)
        self.redo_action.setStatusTip('Redo document changes')
        self.redo_action.triggered.connect(self._editor.redo)

        self.cut_action = QAction('Cu&t', self)
        self.cut_action.setShortcut(cfg.get_shortcut('cut').key_sequence)
        self.cut_action.setStatusTip('Cut to clipboard')
        self.cut_action.triggered.connect(self._editor.cut)

        self.copy_action = QAction('&Copy', self)
        self.copy_action.setShortcut(cfg.get_shortcut('copy').key_sequence)
        self.copy_action.setStatusTip('Copy to clipboard')
        self.copy_action.triggered.connect(self._editor.copy)

        self.paste_action = QAction('&Paste', self)
        self.paste_action.setShortcut(cfg.get_shortcut('paste').key_sequence)
        self.paste_action.setStatusTip('Paste from clipboard')
        self.paste_action.triggered.connect(self._editor.paste)

        self.delete_action = QAction('&Delete', self)
        self.delete_action.setStatusTip('Delete selected text')
        self.delete_action.triggered.connect(self._editor.delete)

        self.select_all_action = QAction('Select &All', self)
        self.select_all_action.setShortcut(cfg.get_shortcut('select_all').key_sequence)
        self.select_all_action.setStatusTip('Select entire text')
        self.select_all_action.triggered.connect(self.on_select_all_action)

        self.indent_action = QAction('Indent Block', self)
        self.indent_action.setStatusTip('Indents the selected lines')
        self.indent_action.triggered.connect(lambda: self._editor.indent(self.line))

        self.unindent_action = QAction('Unindent Block', self)
        self.unindent_action.setShortcut(cfg.get_shortcut('unindent').key_sequence)
        self.unindent_action.setStatusTip('Unindents the selected lines')
        self.unindent_action.triggered.connect(lambda: self._editor.unindent(self.line))

        self.comment_action = QAction('Toggle Comment', self)
        self.comment_action.setShortcut(cfg.get_shortcut('comment').key_sequence)
        self.comment_action.setStatusTip('Toggles Comment for the selected lines')
        self.comment_action.triggered.connect(lambda:self._editor.comment(self.line))

    def on_select_all_action(self):
        """Handle selectAll action."""
        self._editor.selectAll()

    def init_menu(self):
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
        self.find_action = None
        self.find_dialog = None
        self.replace_action = None
        self.replace_dialog = None
        super(MainEditMenu, self).__init__(parent, editor, None, title)

    def init_actions(self):
        """Initializes the actions."""
        super(MainEditMenu, self).init_actions()

        self.find_action = QAction('&Find...', self)
        self.find_action.setShortcut(cfg.get_shortcut('find').key_sequence)
        self.find_action.setStatusTip('Searches the document')
        self.find_action.triggered.connect(self.on_find_action)

        self.replace_action = QAction('&Replace...', self)
        self.replace_action.setShortcut(cfg.get_shortcut('replace').key_sequence)
        self.replace_action.setStatusTip('Replaces a string with another within the document')
        self.replace_action.triggered.connect(self.on_replace_action)

    def init_menu(self):
        """Initializes the menu user interface."""
        super(MainEditMenu, self).init_menu()
        self.addSeparator()
        self.addAction(self.find_action)
        self.addAction(self.replace_action)

    def on_find_action(self):
        """Handles the find action."""
        self._editor.show_find_replace_dialog(replace_visible=False)

    def on_replace_action(self):
        """Handles the replace action."""
        self._editor.show_find_replace_dialog(replace_visible=True)
