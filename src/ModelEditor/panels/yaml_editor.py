from data.meconfig import MEConfig as cfg
import data.data_node as dn
import helpers.subyaml_change_analyzer as analyzer
from helpers.editor_appearance import EditorAppearance as appearance
from data.data_node import Position
from PyQt5.Qsci import QsciScintilla, QsciLexerYAML, QsciAPIs
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import icon


class YamlEditorWidget(QsciScintilla):
    """
    Main editor widget for editing yaml file

    Events:
        :ref:`cursorChanged <cursor_changed>`
        :ref:`nodeChanged <node_changed>`
        :ref:`structureChanged <structure_changed>`
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
    errorMarginClicked = QtCore.pyqtSignal(int)
    """
    .. _error_margin_clicked:
    Signal is sent when margin with error icon is clicked.

    parameter: line number in text document
    """

    def __init__(self, parent=None):
        super(YamlEditorWidget, self).__init__(parent)

        appearance.set_default_appearens(self)

        # Set Yaml lexer
        self._lexer = QsciLexerYAML()
        self._lexer.setFont(appearance.DEFAULT_FONT)
        self.setLexer(self._lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1)

        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setTabWidth(2)
        self.setUtf8(True)

        self._lexer.setColor(QtGui.QColor("#aa0000"), QsciLexerYAML.SyntaxErrorMarker)
        self._lexer.setPaper(QtGui.QColor("#ffe4e4"), QsciLexerYAML.SyntaxErrorMarker)

        # Completetion
        self._api = QsciAPIs(self._lexer)
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
        self.setMarkerBackgroundColor(QtGui.QColor("#a50505"), 4 + dn.DataError.Severity.fatal.value)
        self.setMarkerBackgroundColor(QtGui.QColor("#ee4c4c"), 4 + dn.DataError.Severity.error.value)
        self.setMarkerBackgroundColor(QtGui.QColor("#FFAC30"), 4 + dn.DataError.Severity.warning.value)
        self.setMarkerBackgroundColor(QtGui.QColor("#3399FF"), 4 + dn.DataError.Severity.info.value)

        # signals
        self.marginClicked.connect(self._margin_clicked)
        self.cursorPositionChanged.connect(self._cursor_position_changed)
        self.textChanged.connect(self._text_changed)
        self._pos = editorPosition()

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
        if cfg.document != self.text():
            self.setText(cfg.document)
        self._reload_margin()

    def _cursor_position_changed(self, line, index):
        """Function for cursorPositionChanged signal"""
        if self._pos.new_pos(self, line, index):
            if self._pos.is_changed:
                self.structureChanged.emit(line + 1, index + 1)
            else:
                self.nodeChanged.emit(line + 1, index + 1)
        else:
            self._pos.make_post_operation(self, line, index)
        self.cursorChanged.emit(line + 1, index + 1)

    def _text_changed(self):
        """Function for textChanged signal"""
        self._pos.new_array_line_completation(self)
        self._pos.spec_char_completation(self)
        if not self._pos.fix_bounds(self):
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
        self._old_text = [""]
        """All yaml text before changes"""
        self._last_line = ""
        """last cursor text of line for comparison"""
        self._last_line_after = None
        """last after cursor text of line for comparison"""
        self._to_end_line = True
        """Bound max position is to end line"""
        self._key_and_value = False
        """Bound max position is to end line"""
        self._new_array_item = False
        """make new array item operation"""
        self._spec_char = ""
        """make special char operation"""

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
            if self._spec_char == " ":
                editor.setCursorPosition(line, index + 1)
            self._spec_char = ""

    def spec_char_completation(self, editor):
        """if is added special char, set text for completation else empty string"""
        new_line = editor.text(self.line)
        if len(self._last_line) + 1 == len(new_line):
            line, index = editor.getCursorPosition()
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
                if new_line[index] == ':' or new_line[index] == ',':
                    self._spec_char = " "

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
            anal = self._init_analyzer(editor, line, index)
            pos_type = anal.get_pos_type()
            # value or key changed and cursor is in opposite
            if self._key_and_value and self.begin_line == self.line:
                if pos_type is analyzer.PosType.in_key:
                    if self.is_value_changed:
                        return True
            if pos_type is analyzer.PosType.in_value:
                if self.is_key_changed:
                    return True
            if pos_type is not analyzer.PosType.in_inner:
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
                        type(self.node) != dn.ScalarNode):
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
        anal = self._init_analyzer(editor, self.line, self.index)
        # value and key changed and cursor is in opposite
        pos_type = anal.get_pos_type()
        if self._key_and_value and self.begin_line == self.line:
            if pos_type is analyzer.PosType.in_key:
                self.is_key_changed = True
                if self.is_value_changed:
                    return False
        if pos_type is analyzer.PosType.in_value:
            self.is_value_changed = True
            if self.is_key_changed:
                return False
        return True

    def _reload_autocompletation(self, editor):
        """New line was added"""
        editor._api.clear()
        for option in self.node.options:
            editor._api.add(option)
        editor._api.prepare()

    def node_init(self, node, editor):
        """set new node"""
        self.node = node
        if node is not None:
            self.begin_index = node.start.column - 1
            self.begin_line = node.start.line - 1
            self.end_index = node.end.column - 1
            self.end_line = node.end.line - 1
            self._key_and_value = type(node) == dn.ScalarNode
        else:
            self.begin_line = 0
            self.begin_index = 0
            self.end_line = 0
            self.end_index = 0
        self.is_changed = False
        self.is_value_changed = False
        self.is_key_changed = False
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

    def _init_analyzer(self, editor, line, index):
        """prepare data for analyzer, and return it"""
        in_line = self.line - self.begin_line
        in_index = self.index
        if self.line == self.begin_line:
            in_index = self.index - self.begin_index
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
