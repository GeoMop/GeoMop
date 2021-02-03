from PyQt5.QtWidgets import QMenu, QAction

from LayerEditor.ui.data.le_model import LEModel


class InterfaceMenu(QMenu):
    def __init__(self, le_model: LEModel, itf_label):
        super(InterfaceMenu, self).__init__()

        if itf_label.fracture_layer is None:
            self.fracture_action = QAction('Add Fracture ...', self)
            self.fracture_action.setStatusTip('Add fracture to this interface')
            self.addAction(self.fracture_action)
        else:
            self.fracture_action = QAction('Remove Fracture', self)
            self.fracture_action.setStatusTip('Remove fracture from this interface')
            self.addAction(self.fracture_action)

        self.split_interface_action = QAction('Split interface', self)
        self.split_interface_action.setStatusTip('Split block into two at this interface')
        self.addAction(self.split_interface_action)
        if len(itf_label.i_node_sets) > 1 or itf_label.layer_above is None or itf_label.layer_below is None:
            self.split_interface_action.setDisabled(True)

        self.change_elevation = QAction('Change Elevation', self)
        self.change_elevation.setStatusTip('Edit elevation value')
        self.addAction(self.change_elevation)

        self.set_surface_action = QAction('Set Surface ...', self)
        self.set_surface_action.setStatusTip('Set interface surface')
        self.addAction(self.set_surface_action)

        if itf_label.layer_above is None:
            self.prepend_layer_action = QAction('Prepend Layer ...', self)
        else:
            self.prepend_layer_action = QAction('Split Layer Above ...', self)
        self.prepend_layer_action.setStatusTip('Add layer above')
        self.addAction(self.prepend_layer_action)

        if itf_label.layer_below is None:
            self.append_layer_action = QAction('Append Layer ...', self)
        else:
            self.append_layer_action = QAction('Split Layer Below ...', self)
        self.append_layer_action.setStatusTip('Add layer below')
        self.addAction(self.append_layer_action)

        # self.remove_interface_top_action = QAction('Remove Interface and Top Layer', self)
        # self.remove_interface_top_action.setStatusTip('Remove Interface and Top Layer')
        # self.addAction(self.remove_interface_top_action)
        # if itf_label.layer_above is None:
        #     self.remove_interface_top_action.setDisabled(True)
        #
        # self.remove_interface_bot_action = QAction('Remove Interface and Bottom Layer', self)
        # self.remove_interface_bot_action.setStatusTip('Remove Interface and Bottom Layer')
        # self.addAction(self.remove_interface_bot_action)
        # if itf_label.layer_below is None:
        #     self.remove_interface_bot_action.setDisabled(True)

