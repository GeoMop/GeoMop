"""
Module contains customized QScintilla editor.
"""

# pylint: disable=invalid-name

from data.meconfig import MEConfig as cfg
import data.data_node as dn
import helpers.subyaml_change_analyzer as analyzer
from helpers.editor_appearance import EditorAppearance as appearance
from data.data_node import Position
from PyQt5.Qsci import QsciScintilla, QsciLexerYAML, QsciAPIs
from PyQt5.QtGui import QColor
import PyQt5.QtCore as QtCore
import icon
from contextlib import ContextDecorator
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
import helpers.keyboard_shortcuts as shortcuts
import re
from ui.menus import EditMenu


class YamlEditorWidget(QsciScintilla):
    """
    Main editor widget for editing yaml file

    Events:
        :ref:`cursorChanged <cursor_changed>`
        :ref:`nodeChanged <node_changed>`
        :ref:`structureChanged <structure_changed>`
        :ref:`elementChanged <element_changed>`
        :ref:`errorMarginClicked <error_margin_clicked>`
    """
    cursorChanged = QtCore.pyqtSignal(int, int)
    """
    .. _cursor_changed:
    Signal is sent when cursor position is changed.
    """

    nodeChanged = QtCore.pyqtSignal(int, int)
    """
    .. _node_changed:
    Signal is sent when node below cursor position is changed.
    """

    structureChanged = QtCore.pyqtSignal(int, int)
    """
    .. _structure_changed:
    Signal is sent when node structure document is changed.
    Reload and check is need
    """
    elementChanged = QtCore.pyqtSignal(int, int)
    """
    .. _element_changed:
    Signal is sent when yaml elemt below cursor is changed.
    """
    errorMarginClicked = QtCore.pyqtSignal(int)
    """
    .. _error_margin_clicked:
    Signal is sent when margin with error icon is clicked.

    parameter: line number in text document
    """


    def __init__(self, parent=None):
        super(YamlEditorWidget, self).__init__(parent)

        self.reload_chunk = ReloadChunk()
        """
        reload chunk is a context manager used to make multiple text changes without
        triggering a reload function
        """

        appearance.set_default_appearens(self)

        # Set Yaml lexer
        self._lexer = QsciLexerYAML()
        self._lexer.setFont(appearance.DEFAULT_FONT)
        self.setLexer(self._lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1)

        # editor behavior
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setBackspaceUnindents(True)
        self.setTabIndents(True)
        self.setTabWidth(2)
        self.setUtf8(True)

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

        # Completetion
        self.api = QsciAPIs(self._lexer)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        self.setAutoCompletionThreshold(1)

        # not too small
        self.setMinimumSize(600, 450)

        # Clickable margin 1 for showing markers
        self.setMarginSensitivity(1, True)
        self.setMarginWidth(1, 20)
        self.setMarginMarkerMask(1, 0xF)
        self.markerDefine(icon.get_pixmap("fatal", 16), dn.DataError.Severity.fatal.value)
        self.markerDefine(icon.get_pixmap("error", 16), dn.DataError.Severity.error.value)
        self.markerDefine(icon.get_pixmap("warning", 16), dn.DataError.Severity.warning.value)
        self.markerDefine(icon.get_pixmap("information", 16), dn.DataError.Severity.info.value)

        # Nonclickable margin 2 for showing markers
        self.setMarginWidth(2, 4)
        self.setMarginMarkerMask(2, 0xF0)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + dn.DataError.Severity.fatal.value)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + dn.DataError.Severity.error.value)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + dn.DataError.Severity.warning.value)
        self.markerDefine(QsciScintilla.SC_MARK_FULLRECT, 4 + dn.DataError.Severity.info.value)
        self.setMarkerBackgroundColor(QColor("#a50505"), 4 + dn.DataError.Severity.fatal.value)
        self.setMarkerBackgroundColor(QColor("#ee4c4c"), 4 + dn.DataError.Severity.error.value)
        self.setMarkerBackgroundColor(QColor("#FFAC30"), 4 + dn.DataError.Severity.warning.value)
        self.setMarkerBackgroundColor(QColor("#3399FF"), 4 + dn.DataError.Severity.info.value)

        # signals
        self.reload_chunk.onExit.connect(self._reload_chunk_onExit)
        self.marginClicked.connect(self._margin_clicked)
        self.cursorPositionChanged.connect(self._cursor_position_changed)
        self.textChanged.connect(self._text_changed)
        self._pos = editorPosition()

        # disable QScintilla keyboard shorcuts to handle them in Qt
        for __, shortcut in shortcuts.SCINTILLA.items():
            self.SendScintilla(QsciScintilla.SCI_ASSIGNCMDKEY, shortcut.scintilla_code, 0)

        # begin undo
        self.beginUndoAction()

    def setText(self, text, keep_history=False):
        """
        Sets editor text. Editor history is preserved if `keep_history` is set to True.
        """
        if keep_history:
            # replace all text instead
            self.selectAll()
            self.replaceSelectedText(text)
        else:
            self.endUndoAction()
            super(YamlEditorWidget, self).setText(text)
            self.beginUndoAction()

    def mark_selected(self, start_column, start_row, end_column, end_row):
        """mark area as selected and set cursor to end position"""
        self.setSelection(start_row - 1, start_column - 1, end_row - 1, end_column - 1)

    def set_new_node(self, node=None):
        if node is None:
            line, index = self.getCursorPosition()
            node = cfg.get_data_node(Position(line + 1, index + 1))
        self._pos.node_init(node, self)

    def reload(self):
        """reload data from config"""
        self.endUndoAction()
        self.beginUndoAction()
        if cfg.document != self.text():
            self.setText(cfg.document)
        self._reload_margin()

    def get_curr_element_type(self):
        return self._pos.cursore_type_position.value

    def _cursor_position_changed(self, line, index):
        """Function for cursorPositionChanged signal"""
        old_cursore_type_position = self._pos.cursore_type_position
        if self._pos.new_pos(self, line, index):
            if self._pos.is_changed:
                self.structureChanged.emit(line + 1, index + 1)
            else:
                self.nodeChanged.emit(line + 1, index + 1)
        else:
            self._pos.make_post_operation(self, line, index)
            if old_cursore_type_position != self._pos.cursore_type_position:
                self.elementChanged.emit(self._pos.cursore_type_position.value,
                                         old_cursore_type_position.value)
        self.cursorChanged.emit(line + 1, index + 1)

    def _text_changed(self):
        """Function for textChanged signal"""
        if not self.reload_chunk.freeze_reload:
            self._pos.new_array_line_completation(self)
            self._pos.spec_char_completation(self)
            if not self._pos.fix_bounds(self):
                line, index = self.getCursorPosition()
                self.structureChanged.emit(line + 1, index + 1)

    def _reload_chunk_onExit(self):
        """Emits a structure change upon closing a reload chunk."""
        line, index = self.getCursorPosition()
        self.structureChanged.emit(line + 1, index + 1)

    def _margin_clicked(self, margin, line, modifiers):
        """Margin clicked signal"""
        if (0xF & self.markersAtLine(line)) != 0:
            self.errorMarginClicked.emit(line + 1)

    def _reload_margin(self):
        """Set error icon and mark to margin"""
        self.markerDeleteAll()
        for error in cfg.errors:
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

    def keyPressEvent(self, event):
        """Modifies behavior to handle custom keyboard shortcuts."""
        if event.type() != QtCore.QEvent.KeyPress:
            return

        actions = {
            shortcuts.SCINTILLA['INDENT']: self.indent,
            shortcuts.SCINTILLA['UNINDENT']: self.unindent,
            shortcuts.SCINTILLA['CUT']: self.cut,
            shortcuts.SCINTILLA['COPY']: self.copy,
            shortcuts.SCINTILLA['PASTE']: self.paste,
            shortcuts.SCINTILLA['UNDO']: self.undo,
            shortcuts.SCINTILLA['REDO']: self.redo,
            shortcuts.SCINTILLA['COMMENT']: self.comment,
            shortcuts.SCINTILLA['DELETE']: self.delete,
            shortcuts.SCINTILLA['SELECT_ALL']: self.selectAll,
        }

        for shortcut, action in actions.items():
            if shortcut.matches_key_kvent(event):
                action()
                return

        return super(YamlEditorWidget, self).keyPressEvent(event)

    def indent(self):
        """Indents the selected lines."""
        with self.reload_chunk:
            from_line, from_col, to_line, to_col = self.getSelection()
            if from_line == -1 and to_line == -1:  # no selection -> insert spaces
                spaces = ''.join([' ' * self.tabWidth()])
                self.insertAtCursor(spaces)
            else:  # text selected -> perform indent
                for line in range(from_line, to_line + 1):
                    super(YamlEditorWidget, self).indent(line)
                from_col += self.tabWidth()
                to_col += self.tabWidth()
                self.setSelection(from_line, from_col, to_line, to_col)

    def unindent(self):
        """Unindents the selected lines."""
        from_line, from_col, to_line, to_col = self.getSelection()
        if from_line == -1 and to_line == -1:  # no selection -> unindent current line
            line, col = self.getCursorPosition()
            from_line = to_line = line
            super(YamlEditorWidget, self).unindent(line)
            self.setCursorPosition(line, col - self.tabWidth())
        else:  # selection -> unindent selected lines
            for line in range(from_line, to_line + 1):
                super(YamlEditorWidget, self).unindent(line)
            from_col -= self.tabWidth()
            to_col -= self.tabWidth()
            self.setSelection(from_line, from_col, to_line, to_col)

    def insertAtCursor(self, text):
        """Inserts `text` at cursor position and moves the cursor to the end of inserted text."""
        line, col = self.getCursorPosition()
        self.insertAt(text, line, col)
        text_lines = text.splitlines()
        cursor_line = line + len(text_lines) - 1
        if line == cursor_line:
            cursor_col = col + len(text_lines[0])
        else:
            cursor_col = len(text_lines[-1])
        self.setCursorPosition(cursor_line, cursor_col)

    def setSelectionFromCursor(self, length):
        """Selects `length` characters to the right from cursor."""
        cur_line, cur_col = self.getCursorPosition()
        self.setSelection(cur_line, cur_col, cur_line, cur_col + length)

    def clearSelection(self):
        """Clears current selection."""
        self.setSelectionFromCursor(0)

    def undo(self):
        """Moves back in editing history by a single reload."""
        with self.reload_chunk:
            super(YamlEditorWidget, self).undo()

    def redo(self):
        """Moves forth in editing history by a single reload."""
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
        """Deletes selected text."""
        with self.reload_chunk:
            if not self.hasSelectedText():  # select a single character
                self.setSelectionFromCursor(1)
            super(YamlEditorWidget, self).removeSelectedText()

    def selectAll(self):
        """Selects the entire text."""
        super(YamlEditorWidget, self).selectAll()

    def comment(self):
        """(Un)Comments the selected lines."""
        with self.reload_chunk:
            from_line, __, to_line, __ = self.getSelection()
            if from_line == -1 and to_line == -1:  # no selection -> current line
                cur_line, __ = self.getCursorPosition()
                from_line = to_line = cur_line

            # prepare lines with and without comment
            is_comment = True
            comment_re = re.compile(r'(\s*)# ?(.*)')
            lines_without_comment = []
            lines_with_comment = []
            for line in range(from_line, to_line + 1):
                text = self.text(line).replace('\n', '')
                match = comment_re.match(text)
                lines_with_comment.append('# ' + text)
                if not match:
                    is_comment = False
                else:
                    lines_without_comment.append(match.group(1) + match.group(2))

            # replace the selection with the toggled comment
            self.setSelection(from_line, 0, to_line + 1, 0)  # select entire text
            if is_comment:  # check if comment is applied to all lines
                lines_without_comment.append('')
                self.replaceSelectedText('\n'.join(lines_without_comment))
            else:  # not a comment already - prepend all lines with '# '
                lines_with_comment.append('')
                self.replaceSelectedText('\n'.join(lines_with_comment))

    @pyqtSlot(str, bool, bool, bool)
    def findRequested(self, search_term, is_regex, is_case_sensitive, is_word):
        """Handles find requested event."""
        cur_line, cur_col = self.getCursorPosition()
        self.clearSelection()
        self.findFirst(search_term, is_regex, is_case_sensitive, is_word, True, line=cur_line,
                       index=cur_col)

    @pyqtSlot(str, str, bool, bool, bool)
    def replaceRequested(self, search_term, replacement, is_regex, is_case_sensitive, is_word):
        """Handles replace requested event."""
        with self.reload_chunk:
            if self.hasSelectedText():
                self.replaceSelectedText(replacement)

            self.findRequested(search_term, is_regex, is_case_sensitive, is_word)

    @pyqtSlot(str, str, bool, bool, bool)
    def replaceAllRequested(self, search_term, replacement, is_regex, is_case_sensitive, is_word):
        """Handles replace all requested event."""
        with self.reload_chunk:
            self.clearSelection()
            self.findFirst(search_term, is_regex, is_case_sensitive, is_word, False)

            while self.hasSelectedText():
                self.replaceSelectedText(replacement)
                self.findNext()

    def contextMenuEvent(self, event):
        """Override default context menu of Scintilla."""
        context_menu = EditMenu(self, self)
        context_menu.exec_(event.globalPos())
        event.accept()


class ReloadChunk(ContextDecorator, QObject):
    """
    Class represents a sequence of editor changes that are clumped together to form a single
    reload event. Note that reload should be prevented from occurring while
    `ReloadChunk.freeze_reload` is set to True.

    This class is used by the `YamlEditorWidget` class using the with statement::

        reload_chunk = ReloadChunk()
        with reload_chunk:
            # perform multiple changes
            # reload_chunk.freeze_reload prevents reload changes during editing
        # upon exit, onExit event is triggered (can be connected to textChanged)
    """

    onEnter = pyqtSignal()
    """signal is triggered when reload chunk is opened"""

    onExit = pyqtSignal()
    """signal is triggered when reload chunk is closed"""

    freeze_reload = False
    """indicates whether reload function should be frozen"""

    def __enter__(self):
        self.freeze_reload = True
        self.onEnter.emit()
        return self

    def __exit__(self, *exc):
        self.freeze_reload = False
        self.onExit.emit()
        return False


class editorPosition():
    """Helper for guarding cursor position above node"""

    def __init__(self):
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
        """last key type possition changed"""
        self._old_text = [""]
        """All yaml text before changes"""
        self._last_line = ""
        """last cursor text of line for comparison"""
        self._last_line_after = None
        """last after cursor text of line for comparison"""
        self._to_end_line = True
        """Bound max position is to end line"""
        self._new_array_item = False
        """make new array item operation"""
        self._spec_char = ""
        """make special char operation"""
        self.fatal = False
        """fatal error node"""
        self.cursore_type_position = None
        """Type of yaml structure below cursor"""

    def new_array_line_completation(self, editor):
        """New line was added"""
        if editor.lines() > len(self._old_text) and editor.lines() > self.line + 1:
            pre_line = editor.text(self.line)
            index = pre_line.find("- ")
            if index > -1:
                self._new_array_item = True

    def make_post_operation(self, editor, line, index):
        """complete specion chars after update"""
        if self._new_array_item and editor.lines() > line:
            pre_line = editor.text(self.line - 1)
            new_line = editor.text(self.line)
            if not analyzer.SubYamlChangeAnalyzer.indent_changed(new_line + 'x', pre_line):
                arr_index = pre_line.find("- ")
                if self.index == len(new_line) and self.index == arr_index:
                    editor.insertAt("- ", line, index)
                    editor.setCursorPosition(line, index + 2)
            self._new_array_item = False
        if self._spec_char != "" and editor.lines() > line:
            editor.insertAt(self._spec_char, line, index)
            self._spec_char = ""

    def spec_char_completation(self, editor):
        """if is added special char, set text for completation else empty string"""
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
        """
        Update position and return true if isn't cursor above node
        or is in inner structure
        """
        if self.node is None:
            return True
        self.line = line
        self.index = index
        self._save_lines(editor)
        if not (self.begin_line > line or self.end_line < line or
                (line == self.begin_line and self.begin_index > index) or
                (line == self.end_line and self.end_index < index)):

            # set cursore_type_position
            anal = self._init_analyzer(editor, line, index)
            pos_type = anal.get_pos_type()
            key_type = None
            if pos_type is analyzer.PosType.in_key:
                key_type = anal.get_key_pos_type()
            self.cursore_type_position = analyzer.CursorType.get_cursor_type(pos_type, key_type)

            # value or key changed and cursor is in opposite
            if pos_type is analyzer.PosType.in_key:
                if self.is_value_changed:
                    return True
                if self.last_key_type is not None:
                    new_key_type = anal.get_key_pos_type()
                    if new_key_type != self.last_key_type:
                        return True
            if pos_type is analyzer.PosType.in_value:
                if self.is_key_changed or self.last_key_type is not None:
                    return True
            if pos_type is analyzer.PosType.in_inner:
                if  self.node.is_child_on_line(line+1):
                    return True
            return False
        return True

    def fix_bounds(self, editor):
        """
        Text is changed, recount bounds

        return:False if recount is unsuccessful, and reload is needed
        """
        if self.node is None:
            return False
        # lines count changed
        if editor.lines() != len(self._old_text):
            return False
        # line after cursor was changed (insert mode and paste)
        if (self._last_line_after is not None and
                editor.lines() > self.line and
                self._last_line_after != editor.text(self.line + 1)):
            return False
        new_line = editor.text(self.line)
        # if indentation change
        if analyzer.SubYamlChangeAnalyzer.indent_changed(new_line, self._old_text[self.line]):
            return False
        # line unchanged
        new_line_un = analyzer.SubYamlChangeAnalyzer.uncomment(new_line)
        old_line_un = analyzer.SubYamlChangeAnalyzer.uncomment(self._old_text[self.line])
        if (new_line == self._old_text[self.line] or
                old_line_un == new_line_un):
            if self.begin_line == self.end_line:
                self.is_changed = False
            # return origin values of end
            if self.end_line == self.line and self.node is not None:
                if (self.node.key.span is not None and
                        not isinstance(self.node, dn.ScalarNode)):
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
        end_pos = 0
        before_pos = 0
        if len(self._last_line) != 0 and len(new_line) != 0:
            while new_line[before_pos] == self._last_line[before_pos]:
                before_pos += 1
                if (len(new_line) == before_pos or
                        len(self._last_line) == before_pos):
                    break
            while new_line[-end_pos] == self._last_line[-end_pos]:
                end_pos += 1
                if (len(new_line) == end_pos or
                        len(self._last_line) == end_pos):
                    break
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
        if pos_type is analyzer.PosType.in_key:
            self.is_key_changed = True
            if self.is_value_changed:
                return False
            new_key_type = anal.get_key_pos_type()
            if self.last_key_type is None:
                self.last_key_type = new_key_type
            elif self.last_key_type != new_key_type:
                return False
        if pos_type is analyzer.PosType.in_value:
            self.is_value_changed = True
            if self.is_key_changed:
                return False
        if  self._old_text[self.line].isspace() or len(self._old_text[self.line]) == 0:
            if anal.is_base_struct(new_line):
                return False
        return True

    def _reload_autocompletation(self, editor):
        """New line was added"""
        editor.api.clear()
        for option in self.node.options:
            editor.api.add(option)
        editor.api.prepare()

    def node_init(self, node, editor):
        """set new node"""
        self.node = node
        if node is not None:
            self.begin_index = node.start.column - 1
            self.begin_line = node.start.line - 1
            self.end_index = node.end.column - 1
            self.end_line = node.end.line - 1
        else:
            self.begin_line = 0
            self.begin_index = 0
            self.end_line = 0
            self.end_index = 0
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
        self.line, self.index = editor.getCursorPosition()
        self._save_lines(editor)
        if node is not None:
            self._reload_autocompletation(editor)
        # set cursore_type_position
        anal = self._init_analyzer(editor, self.line, self.index)
        pos_type = anal.get_pos_type()
        key_type = None
        if pos_type is analyzer.PosType.in_key:
            key_type = anal.get_key_pos_type()
        self.cursore_type_position = analyzer.CursorType.get_cursor_type(pos_type, key_type)

    def _init_analyzer(self, editor, line, index):
        """prepare data for analyzer, and return it"""
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
        return analyzer.SubYamlChangeAnalyzer(in_line, in_index, area)

    def _save_lines(self, editor):
        self._last_line = editor.text(self.line)
        if editor.lines() == self.line + 1:
            self._last_line_after = None
        else:
            self._last_line_after = editor.text(self.line + 1)
