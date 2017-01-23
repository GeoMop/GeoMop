from PyQt5 import QtWidgets


class ImportDialog(QtWidgets.QDialog):
    """Dialog to enter shh password."""

    def __init__(self, parent, path, mj_list, pc):
        """Initializes the class."""
        super(ImportDialog, self).__init__(parent)

        message1 = "Selected workspace ({0}) is not recognized as known one.\n".format(path)
        message1 += "Choose import for establishing recognised multijobs ,or"
        message1 += "cancel for importing analysis without multijobs." 
        self._main_label = QtWidgets.QLabel(message1, self)
        self._main_label.setMinimumSize(85, 40)
        message2 = "Recognized multijobs:"  .format(path)
        self._list_label = QtWidgets.QLabel(message2, self)
        self._list = QtWidgets.QListWidget(self)
        self._list.resize(300,120)
        for key, mj in mj_list.items():            
            self._list.addItem("{0} - {1}".format(mj.preset.analysis , mj.preset.name))
        message3 = "Prefix (for confusing settings):"
        self._prefix_label = QtWidgets.QLabel(message3, self)
        self._prefix_edit = QtWidgets.QLineEdit(self)
        self._prefix_edit.setText(pc)
        
        self._button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._button_box.accepted.connect(self.accept)
        self._button_box.rejected.connect(self.reject)
        self._button_box.button(QtWidgets.QDialogButtonBox.Ok).setText("Import")

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self._main_label)
        main_layout.addWidget(self._list_label)
        main_layout.addWidget(self._list)
        main_layout.addWidget(self._prefix_label)
        main_layout.addWidget(self._prefix_edit)
        main_layout.addWidget(self._button_box)

        self.setLayout(main_layout)

        # qt window settings
        self.setWindowTitle("Import Workspace")
        
    def get_prefix(self):
        """get choose prefix from dialog"""
        text = self._prefix_edit.text()
        return text.strip()
