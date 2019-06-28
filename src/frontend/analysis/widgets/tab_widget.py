import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTabWidget, QStackedWidget

from frontend.analysis.widgets.module_view import ModuleView
from common.analysis.module import Module


class TabWidget(QTabWidget):
    def __init__(self, main_widget, edit_menu, parent=None):
        super(TabWidget, self).__init__(parent)
        self.setTabsClosable(True)
        self.setTabShape(1)
        self.tabCloseRequested.connect(self.on_close_tab)
        self.edit_menu = edit_menu
        self.edit_menu.new_action.triggered.connect(self.add_action)
        self.edit_menu.delete.triggered.connect(self.delete_items)
        #self.edit_menu.add_random.triggered.connect(self.add_random_items)
        self.edit_menu.order_diagram.triggered.connect(self.order_diagram)
        self.currentChanged.connect(self.current_changed)


        self.main_widget = main_widget

        self.module_views = {}

    def _add_tab(self, module_filename, module):
        w = QStackedWidget()
        self.module_views[module_filename] = ModuleView(self, module,self.edit_menu)
        for name, workspace in self.module_views[module_filename].workspaces.items():
            w.addWidget(workspace)

        self.addTab(w, module_filename)

    def change_workspace(self, workspace):
        self.currentWidget().setCurrentWidget(workspace)

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

    def currentWorkspace(self):
        return self.currentWidget().currentWidget()

    def add_action(self):
        self.currentWorkspace().scene.add_action(self.currentWorkspace().scene.new_action_pos)

    def delete_items(self):
        self.currentWorkspace().scene.delete_items()

    def add_random_items(self):
        self.currentWorkspace().scene.add_random_items()

    def order_diagram(self):
        self.currentWorkspace().scene.order_diagram()


