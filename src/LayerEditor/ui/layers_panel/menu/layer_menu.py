from PyQt5.QtWidgets import QMenu, QAction

from LayerEditor.ui.data.le_model import LEModel


class LayerMenu(QMenu):
    """Context menu for layer"""

    def __init__(self, le_model: LEModel, wg_layer):
        super(LayerMenu, self).__init__()
        self.split_action = QAction('Split Layer ...', self)
        self.split_action.setStatusTip('Split layer by new interface')
        self.addAction(self.split_action)

        self.rename_action = QAction('Rename ...', self)
        self.rename_action.setStatusTip('Rename this layer')
        self.addAction(self.rename_action)

        self.del_layer_top = QAction('Delete Layer and Top Interface')
        self.del_layer_top.setStatusTip('Delete Layer and Top Interface')
        self.addAction(self.del_layer_top)
        if (not wg_layer.top_delete or
                wg_layer.layer.is_last_decomp(top=True) or
                len(wg_layer.layer.block.layers_dict) == 1):
            self.del_layer_top.setDisabled(True)

        self.del_layer_bot = QAction('Delete Layer and Bottom Interface')
        self.del_layer_bot.setStatusTip('Delete Layer and Bottom Interface')
        self.addAction(self.del_layer_bot)
        if ( not wg_layer.bot_delete or
                wg_layer.layer.is_last_decomp(top=False) or
                len(wg_layer.layer.block.layers_dict) == 1):
            self.del_layer_bot.setDisabled(True)

        self.del_block_action = QAction('Delete Block', self)
        self.del_block_action.setStatusTip('Delete this block')
        self.addAction(self.del_block_action)
        blocks_model = le_model.blocks_model
        n_blocks = len(blocks_model.blocks)
        if n_blocks <= 1 or n_blocks - 1 > blocks_model.get_sorted_blocks().index(wg_layer.layer.block) > 0:
            self.del_block_action.setDisabled(True)
