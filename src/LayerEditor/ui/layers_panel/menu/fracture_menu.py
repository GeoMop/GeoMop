from PyQt5.QtWidgets import QMenu, QAction


class FractureMenu(QMenu):
    def __init__(self):
        super(FractureMenu, self).__init__()
        self.rename_fracture_action = QAction('Rename Fracture', self)
        self.rename_fracture_action.setStatusTip('Rename this fracture')
        self.addAction(self.rename_fracture_action)

        self.remove_fracture_action = QAction('Remove Fracture', self)
        self.remove_fracture_action.setStatusTip('Remove this fracture')
        self.addAction(self.remove_fracture_action)
