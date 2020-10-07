import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QApplication, QCheckBox, QHBoxLayout

from LayerEditor.ui.layers_panel.wg_interface import WGInterface, InterfaceType
from LayerEditor.ui.layers_panel.joiner import Joiner
from LayerEditor.ui.layers_panel.wg_layer import WGLayer
from LayerEditor.ui.layers_panel.radio_button import RadioButton


def add_margins_around_widget(widget: QWidget,
                              left: int,
                              top: int,
                              right: int,
                              bottom: int,
                              alignment=Qt.AlignCenter) -> QHBoxLayout:
    helper_layout = QHBoxLayout()
    helper_layout.addWidget(widget, alignment=alignment)
    helper_layout.setContentsMargins(left, top, right, bottom)
    return helper_layout


class LayerPanel(QWidget):
    """Represents structure of layers and interfaces from data layer"""
    LINE_WIDTH = 2  # Must be multiple of two! Otherwise artifacts will occur due to rounding after dividing by 2
    LINE_PEN = QPen(Qt.black, LINE_WIDTH)

    def __init__(self, parent=None):
        super(LayerPanel, self).__init__(parent)
        self.main_layout = QGridLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addLayout(add_margins_around_widget(QLabel("View"), 5, 0, 5, 0), 0, 0)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Edit"), 5, 0, 5, 0), 0, 1)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Layer"), 5, 0, 5, 0), 0, 2)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Elevation"), 5, 0, 5, 0), 0, 4)
        self.main_layout.addLayout(add_margins_around_widget(QCheckBox(), 5, 0, 5, 0), 1, 0, Qt.AlignCenter)
        self.main_layout.addWidget(RadioButton(self), 1, 1)
        self.main_layout.addWidget(WGInterface(self, None, InterfaceType.TOP), 1, 2)
        self.main_layout.addWidget(WGLayer(self, "Layer_1"), 2, 2)
        self.main_layout.addWidget(WGInterface(self, None), 3, 2)
        self.main_layout.addWidget(WGLayer(self, "Layer_1"), 4, 2)
        top = WGInterface(self, None, InterfaceType.BOTTOM)
        self.main_layout.addWidget(top, 5, 2)
        middle = WGInterface(self, "Fracture_3", InterfaceType.NONE)
        self.main_layout.addWidget(middle, 6, 2)
        bottom = WGInterface(self, None, InterfaceType.TOP)
        self.main_layout.addWidget(bottom, 7, 2)
        self.main_layout.addWidget(Joiner(self, top, bottom, middle), 5, 3, 3, 1)
        self.main_layout.addWidget(WGLayer(self, "Layer_1"), 8, 2)
        self.main_layout.addWidget(WGInterface(self, "Interface"), 9, 2)
        self.main_layout.addWidget(WGLayer(self, "Layer_1"), 10, 2)
        self.main_layout.addWidget(WGInterface(self, "Interface", InterfaceType.BOTTOM), 11, 2)
        self.setLayout(self.main_layout)
        self.main_layout.setHorizontalSpacing(0)
        self.main_layout.setVerticalSpacing(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setPixelSize(20)
    app.setFont(font)
    widget = LayerPanel()
    widget.show()
    app.exec_()
