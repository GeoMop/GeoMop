from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QDialog

from LayerEditor.ui.layers_panel.dialogs.add_fracture import AddFractureDlg
from LayerEditor.ui.layers_panel.menu.interface_menu import InterfaceMenu


class ElevationLabel(QLabel):
    def __init__(self, le_model, i_node_sets, layer_below, layer_above, fracture=None):
        """ :le_model: LEModel
            :itf: interface which elevation is shoved
            :blocks: all blocks which use this interface (up to 3)
            :fracture: fracture layer if the interface has one
        """
        super(ElevationLabel, self).__init__("{}".format(i_node_sets[0].interface.elevation))
        self.le_model = le_model
        self.layer_above = layer_above
        self.layer_below = layer_below
        self.i_node_sets = i_node_sets
        self.fracture = fracture

        self.setContentsMargins(5, 0, 0, 0)
        self.menu = InterfaceMenu(le_model, self)

        self.menu.fracture_action.triggered.connect(self.add_remove_fracture)
        self.menu.split_interface_action.triggered.connect(self.split_interface)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == Qt.RightButton or event.button() == Qt.LeftButton:
            self.menu.exec_(event.globalPos())

    def add_remove_fracture(self):
        if self.fracture is None:
            if len(self.i_node_sets) == 1:
                self.le_model.add_fracture_layer(self.i_node_sets[0])
            else:
                dlg = AddFractureDlg(self.le_model)
                ret = dlg.exec_()
                if ret == QDialog.Accepted:
                    name = dlg.fracture_name.text()
                    # todo: finish later
        else:
            pass
            # todo: finish later

    def split_interface(self):
        self.le_model.split_interface(self.i_node_sets[0], self.layer_below, self.layer_above)
