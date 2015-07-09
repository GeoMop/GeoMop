from data.meconfig import MEConfig as cfg
from data.data_node import Position
from PyQt5.Qsci import QsciScintilla,  QsciLexerYAML
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore

class YamlEditorWidget(QsciScintilla):
    """
    Main editor widget for editing yaml file

    Events:
        :ref:`nodeChanged <node_changed>`
        :ref:`structureChanged <structure_changed>`
    """
    nodeChanged = QtCore.pyqtSignal(int, int)
    """
    .. _node_changed:
    Sgnal is sent when node below cursor possition changed.
    """
    structureChanged = QtCore.pyqtSignal(int, int)
    """
    .. _structure_changed:
    Sgnal is sent when node structure document is changed.
    Reload and check is need
    """
    
    def __init__(self, parent=None):
        super( YamlEditorWidget, self).__init__(parent)

        # Set the default font
        font = QtGui.QFont()
        font.setFamily('serif')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Current line visible with special background color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QtGui.QColor("#ffe4e4"))

        # Set Yaml lexer
        # Set style for Yaml comments (style number 1) to a fixed-width
        # courier.
        #
        lexer = QsciLexerYAML()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT,1)

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        self.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # not too small
        self.setMinimumSize(600, 450)
        
        #signals
        self.cursorPositionChanged.connect(self._cursor_position_changed)
        self.textChanged.connect(self._text_changed)
        self._pos = editorPosition()

    def mark_selected(self, start_column, start_row,  end_column,  end_row):
        """mark area as selected and set cursor to end possition"""
        self.setSelection(start_row-1, start_column-1, end_row-1, end_column-1)  

    def set_new_node(self):
        line, index = self.getCursorPosition()
        node = cfg.get_data_node(Position(line+1, index+1))        
        self._pos.node_init(node, self)

    def reload(self):
        """reload data from config"""
        if cfg.document != self.text:
            self.setText(cfg.document)
        self.set_new_node()
        
    def _cursor_position_changed(self,  line, index):
        """Function for cursorPositionChanged signal"""
        if not self._pos.new_pos(self, line, index):
            if self._pos.is_changed:
                self.structureChanged.emit(line+1,  index+1)
            else:
                self.nodeChanged.emit(line+1, index+1)
                
    def _text_changed(self):
        """Function for textChanged signal"""
        if not self._pos.fix_bounds(self):
            line, index = self.getCursorPosition()
            self.structureChanged.emit(line+1, index+1)

class editorPosition():
    """Helper for guarding cursor possition above node"""
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
        self._old_text = cfg.document.splitlines(False)
        """All yaml text before changes"""
        self._last_line = ""
        """last cursor text of line for comparision"""
        self._last_line_after = ""
        """last after cursor text of line for comparision"""
        self._to_end_line = False
        """Bound max position is to end line"""        
        
    def new_pos(self, editor,  line, index):
        """Update possition and return if is cursor above node"""
        self.line =  line
        self.index = index
        self._save_lines(editor)
        if(self.begin_line >= line and self.end_line <= line and
           self.begin_index >= index and self.end_index <= index):
            return True
        return False
        
    def fix_bounds(self, editor):
        """
        Text is changed, recount bounds
        
        return:False if recount is unsuccesful, and reload is needed
        """
        # lines count changed        
        if editor.lines() != len(self._old_text):
            return False
        #line after cursor was changed (insert mode and paste)
        if(self._last_line_after is not None and
           editor.lines() > self.line and
           self._last_line_after != editor.text(self.line+1)):
            return False
        new_line = editor.text(self.line)
        #lin unchanged
        if new_line == self._old_text[self.line]:
            if self.begin_line == self.end_line:
                self.is_changed = False
            #return origin values of end
            if self.end_line == self.line and self.node is not None:
                if(self.node.key.section is not None):            
                    self.end_index = self.node.key.section.end.column-1
                else:
                    self.end_index = self.node.span.end.column-1
            self._save_lines(editor)
            return True
        if new_line == self._last_line:
            self._save_lines(editor)
            return True
        # find change area
        self.is_changed = True
        end_pos = 0
        befor_pos = 0
        while new_line[-end_pos-1] == self._last_line[-end_pos-1]:
            end_pos += 1
        while new_line[befor_pos+1] == self._last_line[befor_pos+1]:
            befor_pos += 1
        # changes outside bounds
        if(self.begin_line == self.line and 
           befor_pos < self.begin_index):
            return False   
        if(self.end_line == self.line and
           not self._to_end_line and
           len(self._last_line)-end_pos-1 > (self.end_index)):
            return False
        # new end position
        if self.end_line == self.line:
            if self._to_end_line:
                self.end_line = len(new_line)
            else:
                self.end_line = len(new_line)-end_pos-1
        self._save_lines(editor)
        return True
        
    def node_init(self, node,  editor):
        """set new node"""
        self.node = node
        if node is not None:
            if(node.key.section is not None):            
                self.begin_index = node.key.section.start.column-1
                self.begin_line = node.key.section.start.line-1
                self.end_index = node.key.section.end.column-1
                self.end_line = node.key.section.end.line-1
            else:
                self.begin_index = node.span.start.column-1
                self.begin_line = node.span.start.line-1
                self.end_index = node.span.end.column-1
                self.end_line = node.span.end.line-1            
        else:
            self.begin_line = 0
            self.begin_index = 0
            self.end_line = 0
            self.end_index = 0
        self.is_changed = False
        self._save_lines(editor)
        self._to_end_line = self.end_line+1 == len(self._last_line)
        self._old_text = cfg.document.splitlines(False)
        self.line, self.index = editor.getCursorPosition()
        
    def _save_lines(self,  editor):
        self._last_line = editor.text(self.line)
        if editor.lines() == self.line+1:
            self._last_line_after = None
        else:
            self._last_line_after = editor.text(self.line+1)
