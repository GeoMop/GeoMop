from PyQt5.QtWidgets import QMenu, QAction


class LayerMenu(QMenu):
    """Context menu for layer"""
    def __init__(self):
        super(LayerMenu, self).__init__()
        self.split_action = QAction('Split Layer ...', self)
        self.split_action.setStatusTip('Split layer by new interface')
        self.addAction(self.split_action)

        self.rename_action = QAction('Rename ...', self)
        self.rename_action.setStatusTip('Rename this layer')
        self.addAction(self.rename_action)

