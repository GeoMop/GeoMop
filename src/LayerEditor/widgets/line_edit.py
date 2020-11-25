from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QLineEdit


class LineEdit(QLineEdit):
    def __init__(self, text=""):
        super(LineEdit, self).__init__(text)
        self.valid_text_color = self.palette().color(QPalette.Base)
        self.invalid_text_color = QColor(255, 60, 60)
        self.text_valid = True

    def mark_text_invalid(self):
        if self.text_valid:
            self.setStyleSheet(f"background-color: {self.invalid_text_color.name()}")
            self.text_valid = False

    def mark_text_valid(self):
        if not self.text_valid:
            self.styleSheet()
            self.setStyleSheet(f"background-color: {self.valid_text_color.name}")
            self.text_valid = True
