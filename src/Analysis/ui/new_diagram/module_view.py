from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu, QAction

from src.common.analysis.base import _WorkflowBase


class ModuleView(QTreeWidget):
    on_wf_changed = pyqtSignal()
    def __init__(self, module,  parent=None):
        super(ModuleView, self).__init__(parent)
        self.menu = QMenu()
        self.show_wf = QAction("Show this workflow")
        self.menu.addAction(self.show_wf)
        self.show_wf.triggered.connect(self.change_wf)

        self._module = module
        self._currentWF = None
        self.setHeaderHidden(True)
        self.root_item = QTreeWidgetItem(self, [self._module.name])
        self.doubleClicked.connect(self._double_clicked)
        for name, wf in module.definitions.items():

            self._currentWF = wf
            workflow = QTreeWidgetItem(self.root_item, [name])
            self.curr_wf_item = workflow

            if wf._slots:
                input_parent = QTreeWidgetItem(workflow,["Inputs"])
            for number, slot in wf._slots.items():
                child = QTreeWidgetItem(input_parent,[slot.instance_name])

            if wf._result:
                result_parent = QTreeWidgetItem(workflow, ["Output"])
                QTreeWidgetItem(result_parent, [wf._result.instance_name])

        self.mark_active_wf_item(self.curr_wf_item)

    def change_wf(self):
        curr_item = self.currentItem()
        while curr_item.parent() != self.root_item:
            curr_item = curr_item.parent()

        self.mark_active_wf_item(curr_item)
        current_wf = self.module.definitions.get(curr_item.data(0,0))
        self.current_wf = current_wf


    @property
    def module(self):
        return self._module

    @module.setter
    def module(self, module):
        self._module = module

    @property
    def current_wf(self):
        return self._currentWF

    @current_wf.setter
    def current_wf(self, wf):
        self._currentWF = wf
        self.on_wf_changed.emit()

    def _double_clicked(self, model_index):
        if model_index.parent().data() == "Inputs":
            action = self._currentWF.scene.get_action(model_index.data)
            self._currentWF.centerOn(action)

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
