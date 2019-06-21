from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction

from src.common.analysis.action_workflow import _Workflow
from .workspace import Workspace


class ModuleView(QTreeWidget):
    workspace_changed = pyqtSignal(int)
    def __init__(self, tab_widget, module, edit_menu, parent=None):
        super(ModuleView, self).__init__(parent)
        self.tab_widget = tab_widget
        self.menu = QMenu()
        self.show_wf = QAction("Show this workflow")
        self.menu.addAction(self.show_wf)
        self.show_wf.triggered.connect(self.change_workflow)

        self._module = module
        self._current_workspace = None
        self.setHeaderHidden(True)
        self.root_item = QTreeWidgetItem(self, [self._module.name])
        self.doubleClicked.connect(self._double_clicked)

        self.workspaces = {}

        for wf in module.definitions:
            self.workspaces[wf.name] = (Workspace(wf, edit_menu))
            self._current_workspace = self.workspaces[wf.name]
            item = QTreeWidgetItem(self.root_item, [wf.name])
            self.curr_wf_item = item

            if wf.slots:
                input_parent = QTreeWidgetItem(item,["Inputs"])
            for slot in wf.slots:
                child = QTreeWidgetItem(input_parent,[slot.name])

            if wf._result:
                result_parent = QTreeWidgetItem(item, ["Output"])
                QTreeWidgetItem(result_parent, [wf.result.name])

        self.mark_active_wf_item(self.root_item.child(0))

    def change_workflow(self):
        curr_item = self.currentItem()
        while curr_item.parent() != self.root_item:
            curr_item = curr_item.parent()

        self.mark_active_wf_item(curr_item)
        #current_workspace = self.workspaces.get(curr_item.data(0,0))[1]
        self.set_current_workspace(curr_item.data(0, 0))


    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, module):
        self._module = module

    @property
    def current_workspace(self):
        return self._current_workspace

    def set_current_workspace(self, name):
        self._current_workspace = self.workspaces[name]
        temp = self._current_workspace.workflow
        self.tab_widget.change_workspace(self._current_workspace)

    def _double_clicked(self, model_index):
        if model_index.parent().data() == "Inputs":
            temp = model_index.data()
            action = self._current_workspace.scene.get_action(model_index.data())
            self._current_workspace.centerOn(action)

    def mark_active_wf_item(self, item):
        font = QFont()
        self.curr_wf_item.setFont(0, font)
        font.setBold(True)
        item.setFont(0, font)
        self.curr_wf_item = item

    def contextMenuEvent(self, event):
        """Open context menu on right mouse button click if no dragging occurred."""
        super(ModuleView, self).contextMenuEvent(event)
        if self.currentItem() != self.root_item:
            self.menu.exec_(event.globalPos())
