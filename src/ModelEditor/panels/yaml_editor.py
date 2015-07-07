from data.meconfig import MEConfig as cfg
from PyQt5.Qsci import QsciScintilla,  QsciLexerYAML
import PyQt5.QtGui as QtGui


class YamlEditorWidget(QsciScintilla):
    ARROW_MARKER_NUM = 8

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

    def mark_selected(self, start_column, start_row,  end_column,  end_row):
        """mark area as selected and set cursor to end possition"""
        self.setSelection(start_row-1, start_column-1, end_row-1, end_column-1)  
        
    def reload(self):
        """reload data from config"""
        self.setText(	cfg.document)
