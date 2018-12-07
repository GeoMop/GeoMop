"""Module contains an edit menu widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
from PyQt5.QtWidgets import QMenu, QAction

from ModelEditor.meconfig import MEConfig as cfg


class EditMenu(QMenu):
    """Context menu for the editor."""

    def __init__(self, parent, editor, title='&Edit'):
        """
        Initializes the class.
        """
        super().__init__(parent)

        self._editor = editor
        self.aboutToShow.connect(self._check_action_availability)

        # dict action_label -> QAction instance
        self._actions = {}
        self.init_menu()

        self.setTitle(title)

    def add_action(self, label, name, tip, slot):
        ac = QAction(label, self)
        shortcut = cfg.get_shortcut(name)
        if shortcut:
            ac.setShortcut(shortcut.key_sequence)
        ac.setStatusTip(tip)
        ac.triggered.connect(slot)
        self._actions[name] = ac
        self.addAction(ac)


    def on_select_all_action(self):
        """Handle selectAll action."""
        self._editor.selectAll()

    def init_menu(self):
        """Initializes the menu user interface."""
        self.add_action(
            label='&Undo', name='undo',tip='Undo document changes', slot=self._editor.undo)
        self.add_action(
            label='&Redo', name='redo', tip='Redo document changes', slot=self._editor.redo)
        self.addSeparator() ###############################
        self.add_action(
            label='Cu&t', name='cut', tip='Cut to clipboard', slot=self._editor.cut)
        self.add_action(
            label='&Copy', name='copy', tip='Copy to clipboard', slot=self._editor.copy)
        self.add_action(
            label='&Paste', name='paste', tip='Paste from clipboard', slot=self._editor.paste)
        self.add_action(
            label='&Delete', name='delete', tip='Delete selected text', slot=self._editor.delete)
        self.addSeparator() ################################
        self.add_action(
            label='Select &All', name='select_all', tip='Select entire text', slot=self.on_select_all_action)

    def _check_action_availability(self):
        """Enable or disable available actions."""
        self._actions['undo'].setEnabled(self._editor.isUndoAvailable())
        self._actions['redo'].setEnabled(self._editor.isRedoAvailable())
        self._actions['cut'].setEnabled(self._editor.hasSelectedText())
        self._actions['paste'].setEnabled(self._editor.hasSelectedText())
        self._actions['delete'].setEnabled(self._editor.hasSelectedText())


class MainEditMenu(EditMenu):
    """
    Represents the main windows edit menu.
    Contains some extra features compared to `EditMenu`.
    """

    def __init__(self, parent, editor, title='&Edit'):
        """Initializes the class."""
        self.parent = parent
        self._editor = editor
        super().__init__(parent, editor, title)

    def init_menu(self):
        """Initializes the menu user interface."""
        super().init_menu()
        self.addSeparator()  ##################################3
        self.add_action(
            label='Indent Block', name='indent', tip='Indents the selected lines', slot=self._editor.indent)
        self.add_action(
            label='Unindent Block', name='unindent', tip='Unindents the selected lines', slot=self._editor.unindent)
        self.add_action(
            label='Toggle Comment', name='comment', tip='Toggles Comment for the selected lines', slot=self._editor.comment)
        self.addSeparator()  ##################################3
        self.add_action(
            label='&Find...', name='find', tip='Search the document.', slot=self.on_find_action)
        self.add_action(
            label='&Replace...', name='replace', tip='Replaces a string with another within the document.', slot=self.on_replace_action)

    def on_find_action(self):
        """Handles the find action."""
        self._editor.show_find_replace_dialog(replace_visible=False)

    def on_replace_action(self):
        """Handles the replace action."""
        self._editor.show_find_replace_dialog(replace_visible=True)
