from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout


class ActionCategory(QWidget):
    def __init__(self):
        super(ActionCategory, self).__init__()
        self.inner_layout = QVBoxLayout()
        self.setLayout(self.inner_layout)
        self.items = []

    def addWidget(self, widget):
        self.inner_layout.addWidget(widget,0,Qt.AlignCenter)
        self.items.append(widget)

