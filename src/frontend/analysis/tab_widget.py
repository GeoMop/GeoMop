import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget

from src.frontend.analysis.module_view import ModuleView
from .workspace import Workspace
from src.common.analysis.module import Module


class TabWidget(QTabWidget):
    def __init__(self, main_widget, edit_menu, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabShape(1)
        self.tabCloseRequested.connect(self.on_close_tab)
        self.edit_menu = edit_menu
        self.edit_menu.new_action.triggered.connect(self.add_action)
        self.edit_menu.delete.triggered.connect(self.delete_items)
        self.edit_menu.add_random.triggered.connect(self.add_random_items)
        self.edit_menu.order_diagram.triggered.connect(self.order_diagram)
        self.currentChanged.connect(self.current_changed)

        self.main_widget = main_widget

        self.module_views = {}

    def _add_tab(self, module_filename, module):
        w = Workspace(module, self)
        self.module_views[module_filename] = ModuleView(module)
        self.addTab(w, module_filename)

    def open_module(self, filename=None):
        if not isinstance(filename, str):
            filename = QtWidgets.QFileDialog.getOpenFileName(self.parent(), "Select Module", os.getcwd())[0]

        module = Module(os.path.join(os.getcwd(), "analysis", filename))
        self._add_tab(os.path.basename(filename), module)

    def current_changed(self, index):
        curr_module = self.module_views[self.tabText(index)]
        curr_module.show()
        self.main_widget.module_dock.setWidget(curr_module)

    def current_view(self):
        return self.module_views[self.tabText(self.currentIndex())]

    def on_close_tab(self, index):
        print(self.currentIndex())
        self.module_views.pop(self.tabText(index), None)
        self.removeTab(index)

    def add_action(self):
        self.currentWidget().scene.add_action(self.currentWidget().scene.new_action_pos)

    def delete_items(self):
        self.currentWidget().scene.delete_items()

    def add_random_items(self):
        self.currentWidget().scene.add_random_items()

    def order_diagram(self):
        self.currentWidget().scene.order_diagram()


