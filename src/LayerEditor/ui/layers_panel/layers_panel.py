import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPen, QFont
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QApplication, QCheckBox, QHBoxLayout, QButtonGroup, \
    QScrollArea

from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.le_model import LEModel
from LayerEditor.ui.layers_panel.elevation_label import ElevationLabel
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


class LayerPanel(QScrollArea):
    """Represents structure of layers and interfaces from data layer"""
    LINE_WIDTH = 2  # Must be multiple of two! Otherwise artifacts will occur due to rounding after dividing by 2
    LINE_PEN = QPen(Qt.black, LINE_WIDTH)

    def __init__(self, le_model: LEModel, parent=None):
        super(LayerPanel, self).__init__(parent)
        self.le_model = le_model
        self.update_layers_panel()

    def update_layers_panel(self):
        h_bar_value = self.horizontalScrollBar().value()
        v_bar_value = self.verticalScrollBar().value()

        widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.radio_button_group = QButtonGroup()

        self.main_layout.addLayout(add_margins_around_widget(QLabel("View"), 5, 0, 5, 0), 0, 0)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Edit"), 5, 0, 5, 0), 0, 1)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Layer"), 5, 0, 5, 0), 0, 2)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Elevation"), 5, 0, 5, 0), 0, 4)

        layer_panel_model = self._make_layer_panel_model(self.le_model)
        layer_panel_model = self._add_types_of_left_joiners(layer_panel_model)
        self._add_interfaces_and_layer_to_panel(layer_panel_model)
        self._add_right_joiners_and_elevation(layer_panel_model)
        for button in self.radio_button_group.buttons():
            if button.parent().block == self.le_model.gui_curr_block:
                button.setChecked(True)

        widget.setLayout(self.main_layout)

        self.main_layout.setHorizontalSpacing(0)
        self.main_layout.setVerticalSpacing(0)
        self.setWidget(widget)

        self.horizontalScrollBar().setValue(h_bar_value)
        self.verticalScrollBar().setValue(v_bar_value)


    def _make_layer_panel_model(self, le_model):
        layer_panel_model = [[le_model.blocks_model.layers[0].top_in]]
        for layer in le_model.blocks_model.layers:
            if layer.is_stratum:
                if isinstance(layer_panel_model[-1][0], LayerItem) or layer_panel_model[-1][0] != layer.top_in:
                    layer_panel_model.append([layer.top_in])
                layer_panel_model.append([layer])
                layer_panel_model.append([layer.bottom_in])
            else:
                if layer_panel_model[-1][0] != layer.top_in:
                    layer_panel_model.append([layer.top_in, layer])
                else:
                    layer_panel_model[-1] = [layer.top_in, layer]
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
                self._add_edit_view(row, item[0].block)
            if isinstance(item[0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                if len(item) == 3:
                    self.main_layout.addWidget(WGInterface(self, item[1].name, item[2]), row, 2)
                else:
                    self.main_layout.addWidget(WGInterface(self, None, item[1]), row, 2)
            else:
                self.main_layout.addWidget(WGLayer(self, item[0]), row, 2)

    def _add_right_joiners_and_elevation(self, layer_panel_model):
        joiner = 0  # successive interface count
        last_interface = None   # None if ast item was layer otherwise last interface
        for row, item in enumerate(layer_panel_model, 1):
            if isinstance(item[0], (InterfaceNodeSetItem, InterpolatedNodeSetItem)):
                # if current item is an interface...
                if last_interface is None:
                    # ... and before it was layer, start counting successive interfaces for this interface
                    last_interface = item[0].interface
                    joiner += 1
                elif last_interface.elevation == item[0].interface.elevation:
                    # ... and it is the same as the interface before, increment successive interface count
                    joiner += 1
                else:
                    # ... and it is different than last interface, join successive interfaces, give them elevation label
                    # and start new count
                    self._add_joiner(joiner, row - 1)
                    elevation = self._construct_elevation_label(joiner, row - 1, layer_panel_model)
                    self.main_layout.addWidget(elevation, row - joiner, 4, joiner, 1)

                    joiner = 1
                    last_interface = item[0].interface
            else:
                # if current item is layer, end count, join successive interfaces if any and give them elevation label
                self._add_joiner(joiner, row - 1)

                elevation = self._construct_elevation_label(joiner, row - 1, layer_panel_model)
                self.main_layout.addWidget(elevation, row - joiner, 4, joiner, 1)
                joiner = 0
                last_interface = None
        self._add_joiner(joiner, row)
        elevation = self._construct_elevation_label(joiner, row, layer_panel_model)
        self.main_layout.addWidget(elevation, row - joiner + 1, 4, joiner, 1)

    def _construct_elevation_label(self, joiner, last_row, layer_panel_model):
        """ Construct elevation label.
            :joiner: number of successive interfaces
            :row: last row with specified interface
            :layer_panel_model: model for layer panel
        """
        fracture = None
        i_node_sets = []
        for idx in range(last_row - joiner, last_row):
            # check if interface has fracture layer
            item = layer_panel_model[idx]
            i_node_sets.append(item[0])

            if isinstance(item[1], LayerItem):
                fracture = item[1]
        if last_row - joiner - 1 >= 0:
            layer_above = layer_panel_model[last_row - joiner - 1][0]
        else:
            layer_above = None

        if last_row < len(layer_panel_model):
            layer_below = layer_panel_model[last_row][0]
        else:
            layer_below = None

        return ElevationLabel(self.le_model, i_node_sets, layer_below, layer_above, fracture)

    def _add_joiner(self, n_join, end_row):
        """ Adds joiner of interfaces
            :n_join: number of interfaces to join
            :end_row: last row to join
        """
        if n_join == 2:
            top = self.main_layout.itemAtPosition(end_row - 1, 2).widget()
            bot = self.main_layout.itemAtPosition(end_row, 2).widget()
            self.main_layout.addWidget(Joiner(self, top, bot), end_row - 1, 3, 2, 1)
        elif n_join == 3:
            top = self.main_layout.itemAtPosition(end_row - 2, 2).widget()
            mid = self.main_layout.itemAtPosition(end_row - 1, 2).widget()
            bot = self.main_layout.itemAtPosition(end_row, 2).widget()
            self.main_layout.addWidget(Joiner(self, top, bot, mid), end_row - 2, 3, 3, 1)
        elif n_join > 3:
            assert False, "This is not right!!! Something is broken."

    def _add_edit_view(self, row, block):
        check_box = QCheckBox()
        check_box.setCursor(Qt.PointingHandCursor)
        self.main_layout.addLayout(add_margins_around_widget(check_box, 5, 2, 5, 0), row, 0)
        radio_button = RadioButton(self, block)
        self.radio_button_group.addButton(radio_button.radio_button)
        self.main_layout.addWidget(radio_button, row, 1)

    def get_current_block(self):
        return self.radio_button_group.checkedButton().block

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setPixelSize(20)
    app.setFont(font)
    widget = LayerPanel()
    widget.show()
    app.exec_()
