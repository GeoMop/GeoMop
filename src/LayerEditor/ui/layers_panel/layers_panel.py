import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QApplication, QCheckBox, QHBoxLayout, QButtonGroup

from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.le_model import LEModel
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

    def __init__(self, le_model: LEModel, parent=None):
        super(LayerPanel, self).__init__(parent)
        self.main_layout = QGridLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.button_group = QButtonGroup()

        self.main_layout.addLayout(add_margins_around_widget(QLabel("View"), 5, 0, 5, 0), 0, 0)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Edit"), 5, 0, 5, 0), 0, 1)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Layer"), 5, 0, 5, 0), 0, 2)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Elevation"), 5, 0, 5, 0), 0, 4)

        self._fill_layers_panel(le_model)





        # self.main_layout.addLayout(add_margins_around_widget(QCheckBox(), 5, 0, 5, 0), 1, 0)
        # radio_button = RadioButton(self)
        # self.button_group.addButton(radio_button.radio_button)
        # self.main_layout.addWidget(radio_button, 1, 1)
        # self.main_layout.addWidget(WGInterface(self, None, InterfaceType.TOP), 1, 2)
        #
        # self.main_layout.addWidget(WGLayer(self, "Layer_1"), 2, 2)
        #
        # self.main_layout.addWidget(WGInterface(self, None), 3, 2)
        #
        # self.main_layout.addWidget(WGLayer(self, "Layer_1"), 4, 2)
        #
        # top = WGInterface(self, None, InterfaceType.BOTTOM)
        # self.main_layout.addWidget(top, 5, 2)
        #
        # self.main_layout.addLayout(add_margins_around_widget(QCheckBox(), 5, 0, 5, 0), 6, 0)
        # radio_button = RadioButton(self)
        # self.button_group.addButton(radio_button.radio_button)
        # self.main_layout.addWidget(radio_button, 6, 1)
        # middle = WGInterface(self, "Fracture_3", InterfaceType.NONE)
        # self.main_layout.addWidget(middle, 6, 2)
        #
        # self.main_layout.addLayout(add_margins_around_widget(QCheckBox(), 5, 0, 5, 0), 7, 0)
        # radio_button = RadioButton(self)
        # self.button_group.addButton(radio_button.radio_button)
        # self.main_layout.addWidget(radio_button, 7, 1)
        # bottom = WGInterface(self, None, InterfaceType.TOP)
        # self.main_layout.addWidget(bottom, 7, 2)
        #
        # self.main_layout.addWidget(Joiner(self, top, bottom, middle), 5, 3, 3, 1)
        #
        # self.main_layout.addWidget(WGLayer(self, "Layer_1"), 8, 2)
        #
        # self.main_layout.addWidget(WGInterface(self, "Interface"), 9, 2)
        #
        # self.main_layout.addWidget(WGLayer(self, "Layer_1"), 10, 2)
        #
        # self.main_layout.addWidget(WGInterface(self, "Interface", InterfaceType.BOTTOM), 11, 2)

        self.setLayout(self.main_layout)
        self.main_layout.setHorizontalSpacing(0)
        self.main_layout.setVerticalSpacing(0)

    def _fill_layers_panel(self, le_model):
        layer_panel_model = self._make_layer_panel_model(le_model)
        layer_panel_model = self._add_types_of_left_joiners(layer_panel_model)
        self._add_interfaces_and_layer_to_panel(layer_panel_model)
        self._add_right_joiners(layer_panel_model)

    def _make_layer_panel_model(self, le_model):
        layer_panel_model = [[le_model.blocks_model.layers[0].top_top]]
        for layer in le_model.blocks_model.layers:
            if layer.is_stratum:
                if isinstance(layer_panel_model[-1][0], LayerItem) or layer_panel_model[-1][0] != layer.top_top:
                    layer_panel_model.append([layer.top_top])
                layer_panel_model.append([layer])
                layer_panel_model.append([layer.bottom_top])
            else:
                if layer_panel_model[-1][0] != layer.top_top:
                    layer_panel_model.append([layer.top_top, layer])
                else:
                    layer_panel_model[-1] = [layer.top_top, layer]
        return layer_panel_model

    def _add_types_of_left_joiners(self, layer_panel_model):
        layer_panel_model[0].append(InterfaceType.TOP)
        for i in range(1, len(layer_panel_model) - 1):
            type = 3
            if isinstance(layer_panel_model[i][0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                if isinstance(layer_panel_model[i - 1][0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                    if layer_panel_model[i - 1][0].block == layer_panel_model[i][0].block:
                        type -= 2
                else:
                    type -= 2
                if isinstance(layer_panel_model[i + 1][0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                    if layer_panel_model[i + 1][0].block == layer_panel_model[i][0].block:
                        type -= 1
                else:
                    type -= 1
                layer_panel_model[i].append(type)

        layer_panel_model[-1].append(InterfaceType.BOTTOM)
        return layer_panel_model

    def _add_interfaces_and_layer_to_panel(self, layer_panel_model):
        for row, item in enumerate(layer_panel_model, start=1):
            if isinstance(item[0], InterfaceNodeSetItem):
                self.main_layout.addLayout(add_margins_around_widget(QCheckBox(), 5, 0, 5, 0), row, 0)
                radio_button = RadioButton(self)
                self.button_group.addButton(radio_button.radio_button)
                self.main_layout.addWidget(radio_button, row, 1)
            if isinstance(item[0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                if len(item) == 3:
                    self.main_layout.addWidget(WGInterface(self, item[1].name, item[2]), row, 2)
                else:
                    self.main_layout.addWidget(WGInterface(self, None, item[1]), row, 2)
            else:
                self.main_layout.addWidget(WGLayer(self, item[0].name), row, 2)

    def _add_right_joiners(self, layer_panel_model):
        joiner = 0
        last_elevation = None
        for row, item in enumerate(layer_panel_model, 1):
            if isinstance(item[0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                if last_elevation is None:
                    last_elevation = item[0].interface.elevation
                    joiner += 1
                elif last_elevation == item[0].interface.elevation:
                    joiner += 1
                else:
                    self._add_joiner(joiner, row)
                    joiner = 1
                    last_elevation = item[0].interface.elevation
            else:
                self._add_joiner(joiner, row)
                joiner = 0
                last_elevation = None

    def _add_joiner(self, n_join, end_row):
        if n_join == 2:
            top = self.main_layout.itemAtPosition(end_row - 2, 2).widget()
            bot = self.main_layout.itemAtPosition(end_row - 1, 2).widget()
            self.main_layout.addWidget(Joiner(self, top, bot), end_row - 2, 2, 3, 1)
        elif n_join == 3:
            top = self.main_layout.itemAtPosition(end_row - 3, 2).widget()
            mid = self.main_layout.itemAtPosition(end_row - 2, 2).widget()
            bot = self.main_layout.itemAtPosition(end_row - 1, 2).widget()
            self.main_layout.addWidget(Joiner(self, top, bot, mid), end_row - 3, 3, 3, 1)
        elif n_join > 3:
            assert False, "This is not right!!! Something is broken."
    def _add_edit_view(self, row):
        self.main_layout.addLayout(add_margins_around_widget(QCheckBox(), 5, 2, 5, 0), row, 0)
        radio_button = RadioButton(self)
        self.button_group.addButton(radio_button.radio_button)
        self.main_layout.addWidget(radio_button, row, 1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setPixelSize(20)
    app.setFont(font)
    widget = LayerPanel()
    widget.show()
    app.exec_()
