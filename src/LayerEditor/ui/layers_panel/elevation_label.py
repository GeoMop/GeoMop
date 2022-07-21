import math

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel, QDialog, QHBoxLayout, QWidget

from LayerEditor.ui.layers_panel.dialogs.add_fracture import AddFractureDlg
from LayerEditor.ui.layers_panel.dialogs.split_layer_dlg import SplitLayerDlg
from LayerEditor.ui.layers_panel.editable_text import EditableText
from LayerEditor.ui.layers_panel.menu.interface_menu import InterfaceMenu


class ElevationLabel(QWidget):
    def __init__(self, parent, i_node_sets, layer_below, layer_above, fracture=None):
        """ :parent: LayerPanel
            :i_node_sets: all i_node_sets which share this interface
            :layer_below: stratum layer below this interface.
            :layer_above: stratum layer above this interface.
            :fracture: fracture layer if the interface has one
        """
        super(ElevationLabel, self).__init__()
        self.setCursor(Qt.PointingHandCursor)
        self._parent = parent
        self.le_model = parent.le_model
        self.layer_above = layer_above
        self.layer_below = layer_below
        self.i_node_sets = i_node_sets
        self.fracture_layer = fracture

        self.layout = QHBoxLayout()
        self.elevation = EditableText("{}".format(i_node_sets[0].interface.elevation))
        self.elevation.text_edit.editingFinished.connect(self.name_finished)
        self.elevation.text_edit.textChanged.connect(self.text_changed)
        self.layout.addWidget(self.elevation)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setContentsMargins(5, 0, 0, 0)
        self.menu = InterfaceMenu(self.le_model, self)

        self.menu.fracture_action.triggered.connect(self.add_remove_fracture)
        self.menu.split_interface_action.triggered.connect(self.split_interface)
        self.menu.change_elevation.triggered.connect(self.change_elevation)
        if self.menu.append_layer_action is not None:
            self.menu.append_layer_action.triggered.connect(self.append_layer)
        if self.menu.prepend_layer_action is not None:
            self.menu.prepend_layer_action.triggered.connect(self.prepend_layer)
        # self.menu.remove_interface_bot_action.triggered.connect(self.del_itf_bot)
        # self.menu.remove_interface_top_action.triggered.connect(self.del_itf_top)

    def name_finished(self):
        if self.is_elevation_valid() and self.elevation.text_label.text() != self.elevation.text_edit.text():
            self.i_node_sets[0].interface.set_elevation(float(self.elevation.text_edit.text()))
            self._parent.update_layers_panel()
        else:
            self.elevation.text_edit.setText(self.elevation.text_label.text())
            self.elevation.finish_editing()
            self.elevation.setToolTip("")

    def text_changed(self):
        if self.is_elevation_valid():
            self.elevation.text_edit.mark_text_valid()
            self.elevation.setToolTip("")
        else:
            self.elevation.text_edit.mark_text_invalid()
            self.elevation.setToolTip("Value invalid")

    def is_elevation_valid(self):
        try:
            elevation = float(self.elevation.text_edit.text())
        except ValueError:
            return False
        if self.layer_above is None:
            top_limit = math.inf
        else:
            top_limit = self.layer_above.top_in.interface.elevation

        if self.layer_below is None:
            bot_limit = -math.inf
        else:
            bot_limit = self.layer_below.bottom_in.interface.elevation

        if top_limit > elevation > bot_limit:
            return True
        else:
            return False

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.RightButton or event.button() == Qt.LeftButton:
            self.menu.exec_(event.globalPos())

    def add_remove_fracture(self):
        if self.fracture_layer is None:
            if len(self.i_node_sets) == 1:
                self.le_model.add_fracture_layer(self.i_node_sets[0])
            else:
                dlg = AddFractureDlg(self.le_model)
                ret = dlg.exec_()
                if ret == QDialog.Accepted:
                    name = dlg.fracture_name.text()
                    if dlg.fracture_position.currentIndex() == 0:
                        self.le_model.add_fracture_layer(self.i_node_sets[0], name)
                    elif dlg.fracture_position.currentIndex() == 2:
                        self.le_model.add_fracture_layer(self.i_node_sets[-1], name)
                    else:
                        self.le_model.add_fracture_to_new_block(self.i_node_sets[0], name)
        else:
            self.le_model.delete_layer(self.fracture_layer)

    def split_interface(self):
        self.le_model.split_interface(self.i_node_sets[0], self.layer_below, self.layer_above)

    def append_layer(self):
        if self.layer_below is not None:
            bot_y = self.layer_below.bottom_in.interface.elevation
            window_title = "Split Layer Below"
        else:
            bot_y = None
            window_title = "Append Layer"
        top_y = self.i_node_sets[0].interface.elevation
        dlg = SplitLayerDlg(top_y, bot_y, self.le_model)
        dlg.setWindowTitle(window_title)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            name = dlg.layer_name.text()
            elevation = float(dlg.elevation.text())
            if self.layer_below is not None:
                self.le_model.split_layer(self.layer_below, name, elevation)
            else:
                if self.fracture_layer is None:
                    last_layer = self.layer_above
                else:
                    last_layer = self.fracture_layer
                self.le_model.append_layer(last_layer, name, elevation)

    def prepend_layer(self):
        if self.layer_above is not None:
            top_y = self.layer_above.top_in.interface.elevation
            window_title = "Split Layer Above"
        else:
            top_y = None
            window_title = "Prepend Layer"
        bot_y = self.i_node_sets[0].interface.elevation
        dlg = SplitLayerDlg(top_y, bot_y, self.le_model)
        dlg.setWindowTitle(window_title)
        ret = dlg.exec_()
        if ret == QDialog.Accepted:
            name = dlg.layer_name.text()
            elevation = float(dlg.elevation.text())
            if self.layer_above is not None:
                self.le_model.split_layer(self.layer_above, name, elevation)
            else:
                if self.fracture_layer is None:
                    first_layer = self.layer_below
                else:
                    first_layer = self.fracture_layer
                self.le_model.prepend_layer(first_layer, name, elevation)

    def del_itf_top(self):
        self.le_model.delete_layer_bot(self.layer_above)

    def del_itf_bot(self):
        self.le_model.delete_layer_top(self.layer_below)

    def change_elevation(self):
        self.elevation.start_editing()
