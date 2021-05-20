from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class AvailableOverlaysWidget(QTreeWidget):
    def __init__(self, parent=None):
        super(AvailableOverlaysWidget, self).__init__(parent)
        self.setColumnCount(1)

        self.addTopLevelItem(QTreeWidgetItem(['test tree 1']))
        self.addTopLevelItem(QTreeWidgetItem(['test tree 2']))
        self.setDragEnabled(True)
        self.setDragDropMode(QTreeWidget.DragOnly)



