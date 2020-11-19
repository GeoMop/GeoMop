from PyQt5.QtWidgets import QMenu, QAction

from LayerEditor.ui.data.le_model import LEModel


class InterfaceMenu(QMenu):
    def __init__(self, le_model: LEModel, itf_label):
        super(InterfaceMenu, self).__init__()

        if itf_label.fracture is None:
            self.fracture_action = QAction('Add Fracture ...', self)
            self.fracture_action.setStatusTip('Add fracture to this interface')
            self.addAction(self.fracture_action)
        else:
            self.fracture_action = QAction('Remove Fracture', self)
            self.fracture_action.setStatusTip('Remove fracture from this interface')
            self.addAction(self.fracture_action)


        self.split_interface_action = QAction('Split interface', self)
        self.split_interface_action.setStatusTip('Change interface type to split')
        self.addAction(self.split_interface_action)
        if len(itf_label.i_node_sets) > 1 or itf_label.layer_above is None or itf_label.layer_below is None:
            self.split_interface_action.setDisabled(True)

        self.set_surface_action = QAction('Set Surface ...', self)
        self.set_surface_action.setStatusTip('Set interface surface')
        self.addAction(self.set_surface_action)

        self.append_layer_action = QAction('Append Layer ...', self)
        self.append_layer_action.setStatusTip('Append layer to the end')
        self.addAction(self.append_layer_action)

        self.prepend_layer_action = QAction('Prepend Layer ...', self)
        self.prepend_layer_action.setStatusTip('Prepend layer to the start')
        self.addAction(self.prepend_layer_action)

        self.remove_interface_action = QAction('Remove Interface', self)
        self.remove_interface_action.setStatusTip('Remove this interface')
        self.addAction(self.remove_interface_action)
