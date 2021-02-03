import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QLineEdit, QApplication, QMessageBox, QSizePolicy, QWidget, QLabel, QHBoxLayout

from LayerEditor.widgets.line_edit import LineEdit


class EditableText(QWidget):
    def __init__(self, text=None):
        super(EditableText, self).__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.text_label = QLabel(text)
        layout.addWidget(self.text_label)
        self.text_edit = LineEdit(text)
        self.text_edit.setFrame(False)
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.finish_editing()

    def start_editing(self):
        self.text_edit.setText(self.text_label.text())
        self.layout().replaceWidget(self.text_label, self.text_edit)
        self.text_label.hide()
        self.text_edit.show()
        self.text_edit.setFocus()

    def finish_editing(self):
        self.text_label.setText(self.text_edit.text())
        self.layout().replaceWidget(self.text_edit, self.text_label)
        self.text_edit.hide()
        self.text_label.show()
