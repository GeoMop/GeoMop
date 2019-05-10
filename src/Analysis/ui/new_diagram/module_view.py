from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class ModuleView(QTreeWidget):
    def __init__(self, module,  parent=None):
        super(ModuleView, self).__init__(parent)
        self.module = module
        self._currentWF = None
        self.setHeaderHidden(True)
        self.root_item = QTreeWidgetItem(self,[self.module.name])
        self.doubleClicked.connect(self._doubleClicked)
        for name, wf in module.definitions.items():
            if self._currentWF is None:
                self._currentWF = wf
            workflow = QTreeWidgetItem(self.root_item,[name])

            if wf._slots:
                input_parent = QTreeWidgetItem(workflow,["Inputs"])
            for number, slot in wf._slots.items():
                child = QTreeWidgetItem(input_parent,[slot.instance_name])

            if wf._result:
                result_parent = QTreeWidgetItem(workflow, ["Output"])
                QTreeWidgetItem(result_parent, [wf._result.instance_name])


    @property
    def currentWF(self):
        return self._currentWF

    def _doubleClicked(self, model_index):
        temp =model_index.data()
        if model_index.parent().data() == "Inputs":
            action = self._currentWF.scene.get_action(model_index.data)
            self._currentWF.centerOn(action)


