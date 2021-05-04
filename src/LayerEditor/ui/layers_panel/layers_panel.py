from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QCheckBox, QHBoxLayout, QButtonGroup, \
    QScrollArea, QMessageBox, QRadioButton

from LayerEditor.ui.data.interface_node_set_item import InterfaceNodeSetItem
from LayerEditor.ui.data.interpolated_node_set_item import InterpolatedNodeSetItem
from LayerEditor.ui.data.layer_item import LayerItem
from LayerEditor.ui.data.le_model import LEModel
from LayerEditor.ui.layers_panel.data.interface_line_data import InterfaceLineData
from LayerEditor.ui.layers_panel.data.layer_line_data import LayerLineData
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

    overlay_diagram_changed = pyqtSignal(int, bool) # pram: block id, is checked?

    def __init__(self, le_model: LEModel, parent=None):
        super(LayerPanel, self).__init__(parent)
        self.le_model = le_model
        self.update_layers_panel()

    def update_layers_panel(self):
        """Makes/remakes most LayerPanel. Scroll is preserved."""
        h_bar_value = self.horizontalScrollBar().value()
        v_bar_value = self.verticalScrollBar().value()

        widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.edit_buttons_group = QButtonGroup()
        self.edit_buttons_group.buttonClicked.connect(self.change_active_decomp)
        self.view_buttons_group = QButtonGroup()
        self.view_buttons_group.setExclusive(False)
        self.view_buttons_group.buttonClicked.connect(self.view_overlay)

        self.main_layout.addLayout(add_margins_around_widget(QLabel("View"), 5, 0, 5, 0), 0, 0)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Edit"), 5, 0, 5, 0), 0, 1)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Layer"), 5, 0, 5, 0), 0, 2)
        self.main_layout.addLayout(add_margins_around_widget(QLabel("Elevation"), 5, 0, 5, 0), 0, 4)

        layer_panel_model = self._make_layer_panel_model(self.le_model)
        layer_panel_model = self._add_types_of_left_joiners(layer_panel_model)
        self._add_interfaces_and_layer_to_panel(layer_panel_model)
        self._add_right_joiners_and_elevation(layer_panel_model)
        for button in self.edit_buttons_group.buttons():
            if button.parent().block == self.le_model.gui_block_selector.value:
                button.click()

        widget.setLayout(self.main_layout)

        self.main_layout.setHorizontalSpacing(0)
        self.main_layout.setVerticalSpacing(0)
        self.setWidget(widget)

        self.horizontalScrollBar().setValue(h_bar_value)
        self.verticalScrollBar().setValue(v_bar_value)

    def _make_layer_panel_model(self, le_model):
        """Compiles list representing rows in LayerPanel from data layer.
            First item in list is only interface or stratum layer.
            Fracture layer is stored on as second item of interface row."""
        layer_panel_model = [InterfaceLineData(le_model.blocks_model.layers[0].top_in)]
        for layer in le_model.blocks_model.layers:
            if layer.is_stratum:
                if isinstance(layer_panel_model[-1], LayerLineData) or layer_panel_model[-1].i_node_set != layer.top_in:
                    layer_panel_model.append(InterfaceLineData(layer.top_in))
                layer_panel_model.append(LayerLineData(layer))
                layer_panel_model.append(InterfaceLineData(layer.bottom_in))
            else:
                if layer_panel_model[-1].i_node_set != layer.top_in:
                    layer_panel_model.append(InterfaceLineData(layer.top_in, layer))
                else:
                    layer_panel_model[-1] = InterfaceLineData(layer.top_in, layer)
        return layer_panel_model

    def _add_types_of_left_joiners(self, layer_panel_model):
        """ Extends data in layer_panel_model. Adds types of joining lines on left side to interface rows.
            Also adds whether layer can be deleted with top or bot interface. This info is not definitive,
            other data may still disable deleting."""
        if len(layer_panel_model) == 1 or not isinstance(layer_panel_model[1], LayerLineData):
            layer_panel_model[0].type = InterfaceType.NONE
        else:
            layer_panel_model[0].type = InterfaceType.TOP
            last_wg_layer_item = None  # starting row of split
            split = 1  # 0 - no split 1 - one interface(possible start of split) 2,3 - split
            for i in range(1, len(layer_panel_model) - 1):
                type = 3
                if isinstance(layer_panel_model[i], InterfaceLineData):
                    if split == 0:
                        last_wg_layer_item = layer_panel_model[i - 1]
                    split += 1
                    if isinstance(layer_panel_model[i - 1], LayerLineData):
                        type -= 2
                    if isinstance(layer_panel_model[i + 1], LayerLineData):
                        type -= 1
                    layer_panel_model[i].type = type
                else:
                    del_enable = split < 2
                    layer_panel_model[i].top_del_enable = del_enable
                    if last_wg_layer_item is not None:
                        last_wg_layer_item.bottom_del_enable = del_enable
                    split = 0

            if isinstance(layer_panel_model[-2], LayerLineData):
                layer_panel_model[-1].type = InterfaceType.BOTTOM
            else:
                layer_panel_model[-1].type = InterfaceType.NONE
        return layer_panel_model

    def _add_interfaces_and_layer_to_panel(self, layer_panel_model):
        """Adds widgets representing layers and interfaces to Layer panel"""
        for row, item in enumerate(layer_panel_model, start=1):
            if isinstance(item, InterfaceLineData):
                if not item.interpolated:
                    self._add_edit_view(row, item.i_node_set.block)

                self.main_layout.addWidget(WGInterface(self, item.fracture, item.type), row, 2)
            else:
                wg_layer = WGLayer(self, item.layer, item.top_del_enable, item.bottom_del_enable)
                self.main_layout.addWidget(wg_layer, row, 2)

    def _add_right_joiners_and_elevation(self, layer_panel_model):
        """Defines right joiners which join concussive unique blocks. Also adds ElevationLabels."""
        joiner = 0  # successive interface count
        last_interface = None   # None if ast item was layer otherwise last interface
        for row, item in enumerate(layer_panel_model, 1):
            if isinstance(item, InterfaceLineData):
                # if current item is an interface...
                if last_interface is None:
                    # ... and before it was layer, start counting successive interfaces for this interface
                    last_interface = item.i_node_set.interface
                    joiner += 1
                elif last_interface.elevation == item.i_node_set.interface.elevation:
                    # ... and it is the same as the interface before, increment successive interface count
                    joiner += 1
                else:
                    # ... and it is different than last interface, join successive interfaces, give them elevation label
                    # and start new count
                    self._add_joiner(joiner, row - 1)
                    elevation = self._construct_elevation_label(joiner, row - 1, layer_panel_model)
                    self.main_layout.addWidget(elevation, row - joiner, 4, joiner, 1)

                    joiner = 1
                    last_interface = item.i_node_set.interface
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
            i_node_sets.append(item.i_node_set)

            if isinstance(item, InterfaceLineData):
                fracture = item.fracture
        if last_row - joiner - 1 >= 0:
            layer_above = layer_panel_model[last_row - joiner - 1].layer
        else:
            layer_above = None

        if last_row < len(layer_panel_model):
            layer_below = layer_panel_model[last_row].layer
        else:
            layer_below = None

        return ElevationLabel(self, i_node_sets, layer_below, layer_above, fracture)

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
        view_button = QCheckBox()
        view_button.setCursor(Qt.PointingHandCursor)
        self.view_buttons_group.addButton(view_button)
        self.main_layout.addLayout(add_margins_around_widget(view_button, 5, 2, 5, 0), row, 0)
        radio_button = RadioButton(self, block, view_button)
        self.edit_buttons_group.addButton(radio_button.radio_button)
        self.main_layout.addWidget(radio_button, row, 1)

    def get_current_block(self):
        return self.edit_buttons_group.checkedButton().block

    def change_active_decomp(self, radio_button: QRadioButton):
        for button in self.view_buttons_group.buttons():
            button.setEnabled(True)
        radio_button = radio_button.parent()
        self.le_model.blocks_model.gui_block_selector.value = radio_button.block
        radio_button.view_button.setDisabled(True)

    def view_overlay(self, radio_button: QRadioButton):
        # self.overlay_diagram_changed.emit(radio_button.parent().block, radio_button.isChecked())
        for button in self.view_buttons_group.buttons():
            button.setChecked(False)
        msg = QMessageBox(self)
        msg.setWindowTitle("Sorry")
        msg.setText("Overlaying not implemented yet...")
        msg.exec_()

