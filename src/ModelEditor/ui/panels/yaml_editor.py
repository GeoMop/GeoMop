"""
Customized QScintilla editor widget.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

# pylint: disable=invalid-name
import icon
from contextlib import ContextDecorator
import math

from PyQt5.Qsci import QsciScintilla, QsciLexerYAML
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets

from meconfig import cfg
from data import DataNode
from helpers import (Notification, AutocompleteContext, LineAnalyzer, ChangeAnalyzer,
                     NodeAnalyzer, shortcuts)
from ui.dialogs import FindReplaceDialog
from ui.menus import EditMenu
from ui.template import EditorAppearance as appearance
from util import Position, PosType, CursorType


class YamlEditorWidget(QsciScintilla):
    """Main editor widget for editing `YAML <http://yaml.org/spec/1.2/spec.html>`_ files.

    pyqtSignals:
        * :py:attr:`cursorChanged(int, int) <cursorChanged>`
        * :py:attr:`nodeChanged(int, int) <nodeChanged>`
        * :py:attr:`structureChanged(int, int) <structureChanged>`
        * :py:attr:`elementChanged(int, int) <elementChanged>`
        * :py:attr:`errorMarginClicked(int) <errorMarginClicked>`
        * :py:attr:`notFound() <notFound>`
        * :py:attr:`nodeSelected(int, int) <nodeSelected>`

    pyqtSlots:
        * :py:attr:`search(str, bool, bool, bool) <search>`
        * :py:attr:`replace_and_search(str, str, bool, bool, bool) <replace_and_search>`
        * :py:attr:`replace_all(str, str, bool, bool, bool) <replace_all>`
    """
    cursorChanged = QtCore.pyqtSignal(int, int)
    """Signal is sent when cursor position has changed.

    :param int line: new line of cursor
    :param int column: new column of cursor
    """

    nodeChanged = QtCore.pyqtSignal(int, int)
    """Signal is sent when node below cursor position has changed.

    :param int line: current line of cursor
    :param int column: current column of cursor
    """

    structureChanged = QtCore.pyqtSignal(int, int)
    """Signal is sent when reload of structure is needed, because it has changed.

    :param int line: current line of cursor
    :param int column: current column of cursor
    """

    elementChanged = QtCore.pyqtSignal(int, int)
    """Signal is sent when YAML element below cursor has changed.

    The different YAML elements can be for example keys, values, tags or anchors.

    :param int new_cursor_type: CursorType value of the new cursor
    :param int old_cursor_type: CursorType value of the previous cursor
    """

    errorMarginClicked = QtCore.pyqtSignal(int)
    """Signal is sent when margin with error icon is clicked.

    :param int line: line number in text document
    """

    nodeSelected = QtCore.pyqtSignal(int, int)
    """Signal is sent when a node is selected, for example by clicking on the margin.

    :param int line: line of the selected node
    :param int column: column of the selected node (first non-whitespace character)
    """

    def __init__(self, parent=None):
        """Initialize the class."""
        super(YamlEditorWidget, self).__init__(parent)

        self.reload_chunk = ReloadChunk()
        """Context manager for undo/redo actions."""

        self._pos = EditorPosition()
        """Helper for monitoring the cursor position."""

        self._valid_bounds = True
        """indicates whether calculated bounds are valid"""

        self._find_replace_dialog = None
        """dialog for find/replace functionality"""

        appearance.set_default_appearence(self)

        # Set Yaml lexer
        self._lexer = QsciLexerYAML()
        self._lexer.setFont(appearance.DEFAULT_FONT)
        self.setLexer(self._lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1)

        # editor behavior
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)
        self.setTabIndents(True)
        self.setTabWidth(2)
        self.setUtf8(True)
        # self.setAutoIndent(True)

        # text wrapping
        self.setWrapMode(QsciScintilla.WrapWord)
        self.setWrapIndentMode(QsciScintilla.WrapIndentIndented)
        self.setWrapVisualFlags(QsciScintilla.WrapFlagNone, QsciScintilla.WrapFlagByBorder)

        # colors
        self._lexer.setColor(QColor("#aa0000"), QsciLexerYAML.SyntaxErrorMarker)
        self._lexer.setPaper(QColor("#ffe4e4"), QsciLexerYAML.SyntaxErrorMarker)
        self.setIndentationGuidesBackgroundColor(QColor("#e5e5e5"))
        self.setIndentationGuidesForegroundColor(QColor("#e5e5e5"))
        self.setCaretLineBackgroundColor(QColor("#f8f8f8"))
        self.setMatchedBraceBackgroundColor(QColor("#feffa8"))
        self.setMatchedBraceForegroundColor(QColor("#0000ff"))
        self.setUnmatchedBraceBackgroundColor(QColor("#fff2f0"))
        self.setUnmatchedBraceForegroundColor(QColor("#ff0000"))

        # not too small
        self.setMinimumSize(600, 200)
        self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # Autocomplete
        self.SendScintilla(QsciScintilla.SCI_AUTOCSETORDER, QsciScintilla.SC_ORDER_CUSTOM)
        cfg.autocomplete_helper.set_editor(self)

        # disable QScintilla keyboard shortcuts to handle them in Qt
        for shortcut_name in shortcuts.SCINTILLA_DISABLE:
            shortcut = cfg.get_shortcut(shortcut_name)
            if shortcut.scintilla_code is not None:
                self.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, shortcut.scintilla_code, 0)

        # Clickable margin 0 to select node in tree
        self.setMarginSensitivity(0, True)

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.setMarginWidth(1, 20)
        self.setMarginMarkerMask(1, 0xF)
        self.markerDefine(icon.get_pixmap("fatal", 16), Notification.Severity.fatal.value)
        self.markerDefine(icon.get_pixmap("error", 16), Notification.Severity.error.value)
        self.markerDefine(icon.get_pixmap("warning", 16), Notification.Severity.warning.value)
        self.markerDefine(icon.get_pixmap("information", 16), Notification.Severity.info.value)

        # Nonclickable margin 2 for showing markers
        self.setMarginWidth(2, 4)
        self.setMarginMarkerMask(2, 0xF0)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + Notification.Severity.fatal.value)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + Notification.Severity.error.value)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + Notification.Severity.warning.value)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + Notification.Severity.info.value)
        self.setMarkerBackgroundColor(QColor("#a50505"), 4 + Notification.Severity.fatal.value)
        self.setMarkerBackgroundColor(QColor("#ee4c4c"), 4 + Notification.Severity.error.value)
        self.setMarkerBackgroundColor(QColor("#FFAC30"), 4 + Notification.Severity.warning.value)
        self.setMarkerBackgroundColor(QColor("#3399FF"), 4 + Notification.Severity.info.value)

        # signals
        self.reload_chunk.onExit.connect(self._reload_chunk_on_exit)
        self.marginClicked.connect(self._margin_clicked)
        self.cursorPositionChanged.connect(self._cursor_position_changed)
        self.textChanged.connect(self._text_changed)
        self.elementChanged.connect(self._on_element_changed)
        self.SCN_AUTOCSELECTION.connect(self._on_autocompletion_selected)

        # start to monitor actions to enable undo/redo
        self.beginUndoAction()

# ------------------------------ PROPERTIES ----------------------------------

    @property
    def pred_parent(self):
        """Return predicted parent if the current node is not in structure yet.

        :return: predicted parent for the newly created node
        :rtype: :py:class:`DataNode <data.data_node.DataNode>` or None
        """
        pred_parent = self._pos.pred_parent
        if pred_parent is not None:
            # crawl up until you find a parent that was not created by reducible_to_key conversion
            while (pred_parent.parent is not None and
                   pred_parent.origin == DataNode.Origin.ac_reducible_to_key):
                pred_parent = pred_parent.parent
        return pred_parent

    @property
    def curr_node(self):
        """Return current node.

        :return: current node (determined by cursor position)
        :rtype: DataNode
        """
        return self._pos.node

    @property
    def cursor_type_position(self):
        """Return cursor type of the current position.

        :return: cursor type indicating position in a YAML node
        :rtype: CursorType
        """
        return self._pos.cursor_type_position.value

    @property
    def eof_cursor(self):
        """Cursor position for end of file."""
        return 1000000, 1000000, 1000000, 1000000

# ------------------------- TEXT MANIPULATION METHODS ------------------------

    def indent(self):
        """Indent the selected line(s).

        If no line is selected, indent the current line.
        """
        from_line, from_col, to_line, to_col = self.getSelection()
        nothing_selected = from_line == -1 and to_line == -1
        if nothing_selected:
            # regular Tab keyPress
            spaces = ''.join([' ' * self.tabWidth()])

            # insert spaces and move the cursor position
            self.insert_at_cursor(spaces)
        else:
            # perform indent
            with self.reload_chunk:
                for line in range(from_line, to_line + 1):
                    super(YamlEditorWidget, self).indent(line)

            # adjust the position of selection
            from_col += self.tabWidth()
            to_col += self.tabWidth()
            self.setSelection(from_line, from_col, to_line, to_col)

    def unindent(self):
        """Unindent the selected line(s).

        If no line is selected, unindent the current line.
        """
        from_line, from_col, to_line, to_col = self.getSelection()
        nothing_selected = from_line == -1 and to_line == -1
        if nothing_selected:
            # unindent current line
            line, col = self.getCursorPosition()
            super(YamlEditorWidget, self).unindent(line)

            # adjust cursor position
            self.setCursorPosition(line, col - self.tabWidth())
        else:
            # unindent selected lines
            for line in range(from_line, to_line + 1):
                super(YamlEditorWidget, self).unindent(line)

            # adjust the position selection
            from_col -= self.tabWidth()
            to_col -= self.tabWidth()
            self.setSelection(from_line, from_col, to_line, to_col)

    def comment(self):
        """Toggle comment for selected lines.

        If no line is selected, toggle comment for current line.
        """
        with self.reload_chunk:
            from_line, __, to_line, __ = self.getSelection()
            nothing_selected = from_line == -1 and to_line == -1
            if nothing_selected:
                # apply to current line
                curr_line, __ = self.getCursorPosition()
                from_line = to_line = curr_line

            # prepare lines with and without comment
            is_comment = True
            lines_without_comment = []
            lines_with_comment = []
            for line_index in range(from_line, to_line + 1):
                line = self.text(line_index).replace('\n', '')
                lines_with_comment.append('# ' + line)
                if LineAnalyzer.begins_with_comment(line):
                    lines_without_comment.append(LineAnalyzer.uncomment(line))
                else:
                    is_comment = False

            # replace the selection with the toggled comment
            self.setSelection(from_line, 0, to_line + 1, 0)  # select entire text
            if is_comment:  # check if comment is applied to all lines
                lines_without_comment.append('')
                self.replaceSelectedText('\n'.join(lines_without_comment))
            else:  # not a comment already - prepend all lines with '# '
                lines_with_comment.append('')
                self.replaceSelectedText('\n'.join(lines_with_comment))

    def undo(self):
        """Undo a single reload."""
        with self.reload_chunk:
            super(YamlEditorWidget, self).undo()

    def redo(self):
        """Redo a single reload."""
        with self.reload_chunk:
            super(YamlEditorWidget, self).redo()

    def copy(self):
        """Copy to clipboard."""
        with self.reload_chunk:
            super(YamlEditorWidget, self).copy()

    def cut(self):
        """Cut to clipboard."""
        with self.reload_chunk:
            super(YamlEditorWidget, self).cut()

    def paste(self):
        """Paste from clipboard."""
        with self.reload_chunk:
            super(YamlEditorWidget, self).paste()

    def delete(self):
        """Delete selected text."""
        if not self.hasSelectedText():  # select a single character
            self.set_selection_from_cursor(1)
        self.remove_selection()

    def setText(self, text, keep_history=False):
        """Set editor text either with or without deleting the editing history.

        :param str text: text to be set in editor
        :param bool keep_history=False: if set to True, history is preserved
        """
        if keep_history:
            # replace all text instead
            self.selectAll()
            self.replaceSelectedText(text)
        else:
            self.endUndoAction()
            super(YamlEditorWidget, self).setText(text)
            self.beginUndoAction()

    def insert_at_cursor(self, text):
        """Insert text at cursor position and move the cursor to the end of inserted text.

        :param str text: text to be inserted
        """
        line, col = self.getCursorPosition()
        self.insertAt(text, line, col)
        text_lines = text.splitlines()
        added_line_count = len(text_lines) - 1
        cursor_line = line + added_line_count
        if line == cursor_line:
            cursor_col = col + len(text_lines[0])
        else:
            cursor_col = len(text_lines[-1])
        self.setCursorPosition(cursor_line, cursor_col)

# ---------------------- SELECTION OPERATIONS ------------------------------

    def mark_selected(self, start_line, start_column, end_line, end_column):
        """Mark area as selected and set cursor to end position.

        :param int start_line: line where the selection starts
        :param int start_column: column where the selection starts
        :param int end_line: line where the selection ends
        :param int end_column: column where the selection ends
        """
        # first call ensures scrolling to the end of the text
        self.setSelection(end_line - 1, end_column - 1, start_line - 1, start_column - 1)
        # the second call places the cursor at the front os selection and makes it visible as well
        self.setSelection(start_line - 1, start_column - 1, end_line - 1, end_column - 1)

    def set_selection_from_cursor(self, length):
        """Select characters from the current cursor position.

        :param int length: amount of characters to select
        """
        cur_line, cur_col = self.getCursorPosition()
        self.setSelection(cur_line, cur_col, cur_line, cur_col + length)

    def clear_selection(self):
        """Clear the current selection."""
        self.set_selection_from_cursor(0)

    def remove_selection(self):
        """Remove the selected text and trigger a cursor changed action."""
        self.removeSelectedText()
        line, index = self.getCursorPosition()
        self._cursor_position_changed(line, index)

# ----------------------------- STRUCTURE RELATED ----------------------------

    def reload(self):
        """Reload data from config."""
        self.endUndoAction()
        self.beginUndoAction()
        if cfg.document != self.text():
            self.setText(cfg.document)
        self._reload_margin()

    def set_new_node(self, node=None):
        """Set new node.

        :param DataNode node: node to set. When node is None, node at the current cursor
           position is selected.
        """
        if node is None:
            line, index = self.getCursorPosition()
            node = cfg.get_data_node(Position(line + 1, index + 1))
        self._pos.node_init(node, self)

# -------------------------- AUTOCOMPLETE ---------------------------------

    @property
    def autocompletion_context(self):
        """Create current autocomplete context."""
        cur_line, cur_col = self.getCursorPosition()
        context_args = LineAnalyzer.get_autocomplete_context(self.text(cur_line), cur_col)
        return AutocompleteContext(*context_args)

    def _on_autocompletion_selected(self, selected, position):
        """Handle autocompletion selection (from QScintilla).

        :param str selected: text of the selected option
        :param int position: index of the beginning of the autocompleted word in the text
        """
        cfg.autocomplete_helper.hide_autocompletion()
        option = selected.decode('utf-8')
        option_text = cfg.autocomplete_helper.get_autocompletion(option)
        text = self.text()
        lines = text[position:]
        line = lines.split('\n')[0]
        word_to_replace = LineAnalyzer.get_autocompletion_word(line)
        end_position = position + len(word_to_replace)
        self.SendScintilla(QsciScintilla.SCI_SETSELECTION, end_position, position)
        with self.reload_chunk:
            self.replaceSelectedText(option_text)

# ---------------------------- FIND / REPLACE --------------------------------

    def show_find_replace_dialog(self, replace_visible=False):
        """Displays or refreshes the find replace dialog.

        :param bool replace_visible: when set to False, replace part of the dialog is hidden
        """
        search_term = ""
        if self._find_replace_dialog is not None and self._find_replace_dialog.isVisible():
            search_term = self._find_replace_dialog.search_term
            self._find_replace_dialog.close()

        self._find_replace_dialog = FindReplaceDialog(self, replace_visible,
                                                      defaults=self._find_replace_dialog)

        # handle current selection
        from_row, from_col, to_row, to_col = self.getSelection()
        if not search_term and from_row == to_row and from_col != to_col:
            # non-empty single line text
            search_term = self.selectedText()
        else:  # multiple lines -> ignore selection
            self.clear_selection()
        if search_term:
            self._find_replace_dialog.search_term = search_term

        # connect actions
        self._find_replace_dialog.search.connect(self.search)
        self._find_replace_dialog.replace.connect(self.replace_and_search)
        self._find_replace_dialog.replace_all.connect(self.replace_all)

        # show and set focus
        self._find_replace_dialog.show()
        self._find_replace_dialog.activateWindow()

        # set position
        top_right_editor = self.mapToGlobal(self.geometry().topRight())
        pos_x = top_right_editor.x() - self._find_replace_dialog.width() - 1
        pos_y = top_right_editor.y() + 1
        self._find_replace_dialog.move(pos_x, pos_y)

    @pyqtSlot(str, bool, bool, bool)
    def search(self, search_term, is_regex, is_case_sensitive, is_word):
        """Search the text for given term.

        :param str search_term: search term
        :param bool is_regex: if set to True, search term is regarded as a regular expression
        :param bool is_case_sensitive: if set to True, the search is case sensitive
        :param bool is_word: if set to True, search only matches entire words
        """
        cur_line, cur_col = self.getCursorPosition()
        self.clear_selection()
        self.findFirst(search_term, is_regex, is_case_sensitive, is_word, True, line=cur_line,
                       index=cur_col)
        if not self.hasSelectedText():
            self._find_replace_dialog.on_match_not_found()
        else:
            self._find_replace_dialog.on_match_found()

    @pyqtSlot(str, str, bool, bool, bool)
    def replace_and_search(self, search_term, replacement, is_regex, is_case_sensitive, is_word):
        """Replace the selected text and perform a search.

        :param str search_term: search term
        :param str replacement: text that will replace result of the search
        :param bool is_regex: if set to True, search term is regarded as a regular expression
        :param bool is_case_sensitive: if set to True, the search is case sensitive
        :param bool is_word: if set to True, search only matches entire words
        """
        with self.reload_chunk:
            if self.hasSelectedText():
                self.replaceSelectedText(replacement)

            self.search(search_term, is_regex, is_case_sensitive, is_word)

    @pyqtSlot(str, str, bool, bool, bool)
    def replace_all(self, search_term, replacement, is_regex, is_case_sensitive, is_word):
        """Replace all occurrences of search results with given text.

        This function will search the text first and only then will be all occurrences be replaced.
        This prevents looping of the function for certain replacements (like a -> aa).

        :param str search_term: search term
        :param str replacement: text that will replace result of the search
        :param bool is_regex: if set to True, search term is regarded as a regular expression
        :param bool is_case_sensitive: if set to True, the search is case sensitive
        :param bool is_word: if set to True, search only matches entire words
        """
        with self.reload_chunk:
            boundaries = []
            self.clear_selection()
            self.setCursorPosition(0, 0)
            self.findFirst(search_term, is_regex, is_case_sensitive, is_word, False)
            if not self.hasSelectedText():
                self._find_replace_dialog.on_match_not_found()

            # find and record all occurrences
            while (self.hasSelectedText() and
                   (len(boundaries) == 0 or boundaries[-1] != self.getSelection())):
                boundaries.append(self.getSelection())
                self.findNext()

            text = ""
            # replace all occurrences by copying the valid parts of text and adding replacement
            # text instead of original occurrence
            for from_b, to_b in zip([(0, 0, 0, 0)] + boundaries, boundaries + [self.eof_cursor]):
                self.setSelection(from_b[2], from_b[3], to_b[0], to_b[1])
                text += self.selectedText() + replacement
            text = text[:-len(replacement)]
            self.setText(text, keep_history=True)

# ------------------------------- MARGIN -------------------------------------

    def _margin_clicked(self, margin, line, modifiers):
        """Handle :py:attr:`marginClicked` signal.

        :param int margin: type of margin
        :param int line: line where margin was clicked:
        :param modifiers: modifiers
        """
        # pylint: disable=unused-argument
        line_has_error = (0xF & self.markersAtLine(line)) != 0
        if line_has_error and margin == 1:  # display error
            self.errorMarginClicked.emit(line + 1)
        else:  # select node in tree
            line_text = self.text(line)
            column = LineAnalyzer.get_node_start(line_text)
            if not column:  # ignore empty lines
                return
            column += 1
            line += 1
            self.nodeSelected.emit(line, column)

    def _reload_margin(self):
        """Set error icons and marks for margin."""
        self.markerDeleteAll()
        for error in cfg.notifications:
            # icon
            line = error.span.start.line - 1
            present = 0xF & self.markersAtLine(line)
            if present < (1 << error.severity.value):
                if present > 0:
                    for i in range(0, 4):
                        if (present & (1 << i)) == (1 << i):
                            self.markerDelete(line, i)
                self.markerAdd(line, error.severity.value)
            # mark
            for line in range(error.span.start.line - 1, error.span.end.line):
                present = (0xF0 & self.markersAtLine(line)) >> 4
                if present < (1 << error.severity.value):
                    if present > 0:
                        for i in range(0, 4):
                            if (present & (1 << i)) == (1 << i):
                                self.markerDelete(line, i + 4)
                self.markerAdd(line, error.severity.value + 4)

# --------------------------- PYQT GUI FUNCTIONALITY -----------------------

    def keyPressEvent(self, event):
        """Handle keyPress behavior to allow custom keyboard shortcuts.

        :param QKeyEvent event: event with the key press information
        """
        if event.type() != QtCore.QEvent.KeyPress:
            return

        actions = [
            ('escape', lambda: self._handle_keypress_escape(event)),
            ('f3', lambda: self._handle_keypress_f3(event)),
            ('tab', lambda: self._handle_keypress_tab(event)),
            ('backspace', lambda: self._handle_keypress_backspace(event)),
            ('delete', self.delete),
            ('copy', self.copy),
            ('paste', self.paste),
            ('cut', self.cut),
            ('undo', self.undo),
            ('redo', self.redo),
            ('select_all', self.selectAll),
            ('show_autocompletion', cfg.autocomplete_helper.show_autocompletion),
            ('unindent', self.unindent),
            ('comment', self.comment),
        ]

        for shortcut_name, action in actions:
            shortcut = cfg.get_shortcut(shortcut_name)
            if shortcut.matches_key_event(event):
                return action()

        return super(YamlEditorWidget, self).keyPressEvent(event)

    def contextMenuEvent(self, event):
        """Override default context menu of Scintilla."""
        context_menu = EditMenu(self, self)
        context_menu.exec_(event.globalPos())
        event.accept()

    def _handle_keypress_backspace(self, event):
        """Handle keyPress event for :kdb:`Backspace`."""
        # select characters to delete if there is no selection
        if not self.hasSelectedText():
            line, column = self.getCursorPosition()
            line_text = self.text(line)
            cur_line_text = line_text[:column]

            # unindent to previous level if there are only whitespaces in front of cursor
            if len(cur_line_text) > 0 and LineAnalyzer.is_empty(cur_line_text):
                indent_char_count = LineAnalyzer.get_indent(line_text)
                indent_level = math.ceil(indent_char_count / self.tabWidth()) - 1
                removed_char_count = indent_char_count - indent_level * self.tabWidth()
                self.set_selection_from_cursor(-removed_char_count)

            else:  # delete a single character
                if column > 0:  # delete from this line
                    self.setSelection(line, column, line, column - 1)
                elif line > 0:  # delete from previous line
                    prev_line = line - 1
                    prev_column = len(self.text(prev_line))
                    self.setSelection(prev_line, prev_column - 1, line, column)
        self.remove_selection()
        cfg.autocomplete_helper.refresh_autocompletion()

    def _handle_keypress_tab(self, event):
        """Handle keyPress event for :kdb:`Tab`."""
        if cfg.autocomplete_helper.visible:
            self.SendScintilla(QsciScintilla.SCI_AUTOCCOMPLETE)
        else:
            self.indent()

    def _handle_keypress_escape(self, event):
        """Handle keyPress event for :kdb:`Esc`."""
        if self._find_replace_dialog is not None and self._find_replace_dialog.isVisible():
            self._find_replace_dialog.close()
        super(YamlEditorWidget, self).keyPressEvent(event)

    def _handle_keypress_f3(self, event):
        """Handle keyPress event for :kdb:`F3`."""
        self._find_replace_dialog.perform_find()

    def sizeHint(self):
        """Return the preferred size of widget."""
        return QtCore.QSize(700, 400)

# ------------------- OTHER SIGNALS AND EVENT HANDLERS -----------------------

    def _cursor_position_changed(self, line, column):
        """Handle :py:attr:`cursorPositionChanged` signal.

        :param int line: line of the new cursor position
        :param int column: column of the new cursor position
        """
        old_cursor_type_position = self._pos.cursor_type_position
        old_pred_parent = self._pos.pred_parent
        self._pos.make_post_operation(self, line, column)
        if not self._valid_bounds:
            self.structureChanged.emit(line + 1, column + 1)
        else:
            if self._pos.new_pos(self, line, column):
                if self._pos.is_changed:
                    self.structureChanged.emit(line + 1, column + 1)
                else:
                    self.nodeChanged.emit(line + 1, column + 1)
            else:
                if (old_cursor_type_position != self._pos.cursor_type_position and \
                        old_cursor_type_position is not None) or \
                   (self._pos.pred_parent != old_pred_parent):
                    self.elementChanged.emit(self._pos.cursor_type_position.value,
                                             old_cursor_type_position.value)
        self.cursorChanged.emit(line + 1, column + 1)
        # autocompletion - show if it is pending or refresh
        if cfg.autocomplete_helper.pending_check:
            cfg.autocomplete_helper.pending_check = False
            if len(self.autocompletion_context.hint) == 1:
                cfg.autocomplete_helper.show_autocompletion()
            else:
                cfg.autocomplete_helper.refresh_autocompletion()
        else:
            cfg.autocomplete_helper.refresh_autocompletion()

    def _text_changed(self):
        """Handle :py:attr:`textChanged` signal."""
        if not self.reload_chunk.freeze_reload:
            self._pos.new_line_completation(self)
            self._pos.spec_char_completation(self)
            self._valid_bounds = self._pos.fix_bounds(self)
            # flag autocompletion to be checked whether to display it or not if it is
            # turned on globally
            if cfg.config.display_autocompletion:
                cfg.autocomplete_helper.pending_check = True

    def _reload_chunk_on_exit(self):
        """Emit a structure change upon closing a reload chunk."""
        line, index = self.getCursorPosition()
        self.structureChanged.emit(line + 1, index + 1)

    def _on_element_changed(self):
        """Handle element changed event."""
        self._pos.reload_autocompletion(self)


class ReloadChunk(ContextDecorator, QObject):
    """Context manager to handle history of undo/redo changes in editor.

    The QScintilla editor will mark an undo/redo change when using some of its functions.
    This class serves to indicate when these changes should be joined together to form a single
    undo/redo change.

    This class is used by the `YamlEditorWidget` class using the with statement::

        reload_chunk = ReloadChunk()
        with reload_chunk:
            # perform multiple changes
            # reload_chunk.freeze_reload prevents reload changes during editing
        # upon exit, onExit event is triggered (can be connected to textChanged)

    pyqt Signals:
        * :py:attr:`onEnter() <onEnter>`
        * :py:attr:`onExit() <onExit>`
    """

    onEnter = pyqtSignal()
    """Signal is triggered when reload chunk is entered"""

    onExit = pyqtSignal()
    """Signal is triggered when reload chunk is closed"""

    def __init__(self):
        """Initialize the class."""
        super(ReloadChunk, self).__init__()
        self.freeze_reload = False
        """Indicates whether reload function should be frozen"""

    def __enter__(self):
        """Handle entering the change block."""
        self.freeze_reload = True
        self.onEnter.emit()
        return self

    def __exit__(self, *exc):
        """Handle exiting the change block."""
        self.freeze_reload = False
        self.onExit.emit()
        return False


class EditorPosition:
    """Helper for guarding cursor position above node.

    The purpose of this class is to limit the reloading of data structure (full parsing) to the
    cases when it is really needed instead of reloading it after any character is written.

    The class also manages autocompletion. It triggers the update of available autocompletion
    options when the context changes. It also handles some trivial autocompletion, like completion
    of braces or a new item of an array.

    After data changes, :py:meth:`fix_bounds` should be called to recalculate the boundaries of
    selected data node. Then :py:meth:`new_pos` can be called to determine if a structure reload
    is needed.
    """

    def __init__(self):
        """Initialize the class."""
        self.node = None
        """DataNode item below cursor"""
        self.line = 0
        """Y cursor position"""
        self.index = 0
        """X cursor position"""
        self.begin_line = 0
        """Y min data node position"""
        self.begin_index = 0
        """X min data node position"""
        self.end_line = 0
        """Y max data node position (by adding or deleting text is changed)"""
        self.end_index = 0
        """X max data node position (by adding or deleting text is changed)"""
        self.is_changed = False
        """Is node changed"""
        self.is_value_changed = False
        """Is value changed"""
        self.is_key_changed = False
        """Is key changed"""
        self.last_key_type = None
        """last key type position changed"""
        self._old_text = [""]
        """All yaml text before changes"""
        self._last_line = ""
        """last cursor text of line for comparison"""
        self._last_line_after = None
        """last after cursor text of line for comparison"""
        self._to_end_line = True
        """Bound max position is to end line"""
        self._new_line_indent = None
        """indentation for  new array item operation"""
        self._old_line_prefix = None
        """indentation for  old array item operation"""
        self._spec_char = ""
        """make special char operation"""
        self.fatal = False
        """fatal error node"""
        self.cursor_type_position = None
        """Type of yaml structure below cursor"""
        self.pred_parent = None
        """Predicted parent node for IST"""

    def new_line_completation(self, editor):
        """Add specific symbols to start of line when new line was added.

        ``_old_line_prefix`` is set to indentation and new array (-)
        symbol if need be.
        """
        if editor.lines() > len(self._old_text) and editor.lines() > self.line + 1:
            pre_line = editor.text(self.line)
            indent = LineAnalyzer.get_indent(pre_line)
            index = pre_line.find("- ")
            if index > -1 and index == indent:
                indent_bullet = ("- " if cfg.config.symbol_completion else "")
                if self.node is None or  \
                   self.node.implementation != DataNode.Implementation.scalar or \
                   (self.node.parent.start.line-1) == self.line:
                    self._new_line_indent = indent*' '+"  "
                else:
                    self._new_line_indent = indent*' ' + indent_bullet
                self._old_line_prefix = indent*' ' + indent_bullet
            else:
                self._new_line_indent = indent*' '
                self._old_line_prefix = indent*' '

    def make_post_operation(self, editor, line, index):
        """Complete special chars after text is updated and
        fix parent if new line is added (new_line_completation
        function is called).
        """
        if self._new_line_indent is not None and editor.lines() > line:
            # after new_line_completation function is called
            pre_line = editor.text(line - 1)
            new_line = editor.text(line)
            # preceding line prefix is unchanged
            if ((new_line.isspace() or len(new_line) == 0) and
                    pre_line[:len(self._old_line_prefix)] == self._old_line_prefix):
                # insert prefix
                editor.insertAt(self._new_line_indent, line, index)
                editor.setCursorPosition(line, index + len(self._new_line_indent))
                # fix parent
                if self.node is not None:
                    na = NodeAnalyzer(self._old_text, self.node)
                else:
                    na = NodeAnalyzer(self._old_text, cfg.root)
                self.pred_parent = na.get_parent_for_unfinished(self.line, self.index,
                                                                editor.text(self.line))
            self._new_line_indent = None
        if cfg.config.symbol_completion and self._spec_char != "" and editor.lines() > line:
            editor.insertAt(self._spec_char, line, index)
            self._spec_char = ""

    def spec_char_completation(self, editor):
        """If a special character was added, set text for completion."""
        new_line = editor.text(self.line)
        if len(self._last_line) + 1 == len(new_line):
            __, index = editor.getCursorPosition()
            if len(new_line) > index:
                self._spec_char = ""
                if new_line[index] == '[':
                    self._spec_char = "]"
                if new_line[index] == '"':
                    self._spec_char = '"'
                if new_line[index] == "'":
                    self._spec_char = "'"
                if new_line[index] == '{':
                    self._spec_char = "}"

    def new_pos(self, editor, line, index):
        """Update position and return true if cursor isn't above node
        or is in inner structure.
        """
        if self.line != line:
            self.handle_line_changed()
        self.line = line
        self.index = index
        self._save_lines(editor)
        if not (self.begin_line > line or self.end_line < line or
                (line == self.begin_line and self.begin_index > index) or
                (line == self.end_line and self.end_index < index)):

            # set cursor_type_position
            anal = self._init_analyzer(editor, line, index)
            pos_type = anal.get_pos_type()
            key_type = None
            if pos_type is PosType.in_key:
                key_type = anal.get_key_pos_type()
            self.cursor_type_position = CursorType.get_cursor_type(pos_type, key_type)
            if (self._old_text[line].isspace() or len(self._old_text[line]) == 0) or \
                (self.node is not None and self.node.origin == DataNode.Origin.error):
                if self.node is not None:
                    na = NodeAnalyzer(self._old_text, self.node)
                else:
                    na = NodeAnalyzer(self._old_text, cfg.root)
                self.pred_parent = na.get_parent_for_unfinished(line, index, editor.text(line))
            else:
                self.pred_parent = None

            # value or key changed and cursor is in opposite
            if pos_type is PosType.in_key:
                if self.is_value_changed:
                    return True
                if self.last_key_type is not None:
                    new_key_type = anal.get_key_pos_type()
                    if new_key_type != self.last_key_type:
                        return True
            if pos_type is PosType.in_value:
                if self.is_key_changed or self.last_key_type is not None:
                    return True
            if pos_type is PosType.in_inner and self.node is not None:
                if self.node.is_child_on_line(line+1):
                    return True
            return False
        return True

    def fix_bounds(self, editor):
        """Recalculate the boundaries of data node after text has changed.

        :return: False if recount is unsuccessful, and reload is needed
        """
        # lines count changed
        if editor.lines() != len(self._old_text):
            return False
        # line after cursor was changed (insert mode and paste)
        if (self._last_line_after is not None and
                editor.lines() > self.line and
                self._last_line_after != editor.text(self.line + 1)):
            # new line and old line is empty (editor add indentation)
            if not ((self._last_line_after.isspace() or len(self._last_line_after) == 0) and
                    (editor.text(self.line + 1).isspace() or len(editor.text(self.line + 1)) == 0)):
                return False
        new_line = editor.text(self.line)
        # if indentation change
        if LineAnalyzer.indent_changed(new_line, self._old_text[self.line]):
            return False
        # line unchanged
        new_line_un = LineAnalyzer.strip_comment(new_line)
        old_line_un = LineAnalyzer.strip_comment(self._old_text[self.line])
        if (new_line == self._old_text[self.line] or
                old_line_un == new_line_un):
            if self.begin_line == self.end_line:
                self.is_changed = False
            # return origin values of end
            if self.end_line == self.line and self.node is not None:
                if (self.node.key.span is not None and
                        self.node.implementation != DataNode.Implementation.scalar):
                    self.end_index = self.node.key.span.end.column - 1
                else:
                    self.end_index = self.node.span.end.column - 1
            self._save_lines(editor)
            return True
        if new_line == self._last_line:
            self._save_lines(editor)
            return True
        # find change area
        self.is_changed = True
        before_pos, end_pos = LineAnalyzer.get_changed_position(new_line, self._last_line)
        # changes outside bounds
        if (self.begin_line == self.line and
                before_pos < self.begin_index):
            return False
        if (self.end_line == self.line and
                not self._to_end_line and
                len(self._last_line) - end_pos - 1 > self.end_index):
            return False
        # new end position
        if self.end_line == self.line:
            if self._to_end_line:
                self.end_index = len(new_line)
            else:
                self.end_index += len(new_line) - len(self._last_line)
        self._save_lines(editor)

        # for delete  is index <> self.index
        line, index = editor.getCursorPosition()
        anal = self._init_analyzer(editor, line, index)
        # value or key changed and cursor is in opposite
        pos_type = anal.get_pos_type()
        if pos_type is PosType.in_key:
            self.is_key_changed = True
            if self.is_value_changed:
                return False
            new_key_type = anal.get_key_pos_type()
            if self.last_key_type is None:
                self.last_key_type = new_key_type
            elif self.last_key_type != new_key_type:
                return False
        # evaluate value changes
        if pos_type is PosType.in_value:
            added_text = new_line[before_pos:len(new_line)-end_pos+1]
            if not added_text.isspace() and added_text not in ['&', '*', '!']:
                self.is_value_changed = True
            if self.is_key_changed:
                return False
        if self._old_text[self.line].isspace() or len(self._old_text[self.line]) == 0:
            if pos_type is PosType.in_key:
                # if added text is space, reload
                if new_line[before_pos:len(new_line)-end_pos+1].isspace():
                    return False
            else:
                if anal. is_base_struct(new_line):
                    return False
        before_pos, end_pos = LineAnalyzer.get_changed_position(new_line, self._old_text[self.line])
        if self.node is not None and self.node.is_jsonchild_on_line(self.line+1):
            if anal.is_basejson_struct(new_line[before_pos:len(new_line)-end_pos+1]):
                return False
        if anal.is_fulljson_struct(new_line[before_pos:len(new_line)-end_pos+1]):
            return False
        return True

    def reload_autocompletion(self, editor):
        """Create new autocomplete options when newline is added."""
        node = None
        if editor.pred_parent is not None:
            node = editor.pred_parent
        elif self.node is not None:
            if self.cursor_type_position == CursorType.key and self.node.parent is not None:
                node = self.node.parent
            else:
                node = self.node

        if node is None or getattr(node, 'input_type', None) is None:
            # use root input type
            input_type = cfg.root_input_type
        else:
            input_type = node.input_type

        cfg.autocomplete_helper.create_options(input_type)
        return True

    def node_init(self, node, editor):
        """Set new node; initializes the EditorPosition class."""
        self.node = node
        self.line, self.index = editor.getCursorPosition()
        if node is not None:
            self.begin_index = node.start.column - 1
            self.begin_line = node.start.line - 1
            self.end_index = node.end.column - 1
            self.end_line = node.end.line - 1
        else:
            self.begin_line = self.line
            self.begin_index = self.index
            self.end_line = self.line
            self.end_index = self.index
        self.is_changed = False
        self.is_value_changed = False
        self.is_key_changed = False
        self.last_key_type = None
        self._to_end_line = self.end_index == len(self._last_line)
        if len(self._last_line) == 0:
            self._to_end_line = True
        self._old_text = cfg.document.splitlines(False)
        if len(self._old_text) + 1 == editor.lines():
            self._old_text.append("")
        self._save_lines(editor)
        # set cursore_type_position
        anal = self._init_analyzer(editor, self.line, self.index)
        pos_type = anal.get_pos_type()
        key_type = None
        if pos_type is PosType.in_key:
            key_type = anal.get_key_pos_type()
        self.cursor_type_position = CursorType.get_cursor_type(pos_type, key_type)

#        if  LineAnalyzer.is_array_char_only(self._old_text[self.line]):
#            self.node = node

        self.pred_parent = None
        if  (self._old_text[self.line].isspace() or len(self._old_text[self.line]) == 0) or \
            (self.node is not None and self.node.origin == DataNode.Origin.error):
            if self.node is not None:
                na = NodeAnalyzer(self._old_text, self.node)
            else:
                na = NodeAnalyzer(self._old_text, cfg.root)
            self.pred_parent = na.get_parent_for_unfinished(self.line, self.index,
                                                            editor.text(self.line))

        # if node is not None:
        #     self.reload_autocompletion(editor)
        self.reload_autocompletion(editor)

    def handle_line_changed(self):
        """Handle when cursor changes line."""
        cfg.autocomplete_helper.hide_autocompletion()

    def _init_analyzer(self, editor, line, index):
        """Prepare data for analyzer, and return it."""
        in_line = line - self.begin_line
        in_index = index
        if line == self.begin_line:
            in_index = index - self.begin_index
        area = []
        for i in range(self.begin_line, self.end_line + 1):
            text = editor.text(i)
            if i == self.end_line:
                text = text[:self.end_index]
            if i == self.begin_line:
                text = text[self.begin_index:]
            area.append(text)
        assert in_line < len(area)
        return ChangeAnalyzer(in_line, in_index, area)

    def _save_lines(self, editor):
        """Save lines."""
        self._last_line = editor.text(self.line)
        if editor.lines() == self.line + 1:
            self._last_line_after = None
        else:
            self._last_line_after = editor.text(self.line + 1)
