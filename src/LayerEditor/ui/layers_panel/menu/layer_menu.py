from PyQt5.QtWidgets import QMenu, QAction

from LayerEditor.ui.data.le_model import LEModel


class LayerMenu(QMenu):
    """Context menu for layer"""
    def __init__(self, le_model: LEModel, layer):
        super(LayerMenu, self).__init__()
        self.split_action = QAction('Split Layer ...', self)
        self.split_action.setStatusTip('Split layer by new interface')
        self.addAction(self.split_action)

        self.rename_action = QAction('Rename ...', self)
        self.rename_action.setStatusTip('Rename this layer')
        self.addAction(self.rename_action)

        self.del_layer_top = QAction('Delete Layer and Top')
        self.del_layer_top.setStatusTip('Delete Layer and Top Interface')
        self.addAction(self.del_layer_top)
        if layer.is_first() or layer.is_last_decomp(top=True):
            self.del_layer_top.setDisabled(True)

        self.del_layer_bot = QAction('Delete Layer and Bottom')
        self.del_layer_bot.setStatusTip('Delete Layer and Bottom Interface')
        self.addAction(self.del_layer_bot)
        if layer.is_last() or layer.is_last_decomp(top=False):
            self.del_layer_bot.setDisabled(True)

        self.del_block_action = QAction('Delete Block', self)
        self.del_block_action.setStatusTip('Delete this block')
        self.addAction(self.del_block_action)
        if len(le_model.blocks_model.blocks) <= 1:
            self.del_block_action.setDisabled(True)
