from PyQt5.QtWidgets import QTabWidget

from .action_editor_menu import ActionEditorMenu


class TabWidget(QTabWidget):
    def __init__(self, edit_menu, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabShape(1)
        self.tabCloseRequested.connect(self.on_close_tab)
        self.edit_menu = edit_menu
        self.edit_menu.new_action.triggered.connect(self.add_action)
        self.edit_menu.delete.triggered.connect(self.delete_items)
        self.edit_menu.add_random.triggered.connect(self.add_random_items)
        self.edit_menu.order.triggered.connect(self.order_diagram)

    def on_close_tab(self, index):
        self.removeTab(index)

    def add_action(self):
        self.currentWidget().scene.add_action()

    def delete_items(self):
        self.currentWidget().scene.delete_items()

    def add_random_items(self):
        self.currentWidget().scene.add_random_items()

    def order_diagram(self):
        self.currentWidget().scene.order_diagram()


