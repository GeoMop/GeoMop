"""
Editor appearance manager.
"""

from PyQt5.Qsci import QsciScintilla
import PyQt5.QtGui as QtGui


class EditorAppearance:
    """Unique editors appearance class"""

    DEFAULT_FONT = QtGui.QFont()

    def __init__(self):
        pass

    @classmethod
    def set_default_appearence(cls, editor):
        """Set default applicatin editor appearents"""
        # Set the default font

        editor.setFont(cls.DEFAULT_FONT)
        editor.setMarginsFont(cls.DEFAULT_FONT)

        # Margin 0 is used for line numbers
        fontmetrics = QtGui.QFontMetrics(cls.DEFAULT_FONT)
        editor.setMarginsFont(cls.DEFAULT_FONT)
        editor.setMarginWidth(0, fontmetrics.width("00000") + 6)
        editor.setMarginLineNumbers(0, True)
        editor.setMarginsBackgroundColor(QtGui.QColor("#cccccc"))

        # Brace matching: enable for a brace immediately before or after
        # the current position
        #
        editor.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        # Don't want to see the horizontal scrollbar at all
        # Use raw message to Scintilla here (all messages are documented
        # here: http://www.scintilla.org/ScintillaDoc.html)
        editor.SendScintilla(QsciScintilla.SCI_SETHSCROLLBAR, 0)

        # Current line visible with special background color
        editor.setCaretLineVisible(True)
        editor.setCaretLineBackgroundColor(QtGui.QColor("#e4e4e4"))

EditorAppearance.DEFAULT_FONT = QtGui.QFont()
EditorAppearance.DEFAULT_FONT.setFamily('Courier')
EditorAppearance.DEFAULT_FONT.setFixedPitch(True)
EditorAppearance.DEFAULT_FONT.setPointSize(11)
