import PyQt5.QtWidgets as QtWidgets


class TranformationDlg(QtWidgets.QDialog):
    def __init__(self, version_list, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Transform format of current document")

        mainVerticalLayout = QtWidgets.QVBoxLayout(self)

        form = QtWidgets.QFormLayout()
        mainVerticalLayout.addLayout(form)

        toVersionLabel = QtWidgets.QLabel("To version:", self)
        self.toVersionComboBox = QtWidgets.QComboBox(self)
        self.toVersionComboBox.addItems(version_list)
        form.addRow(toVersionLabel, self.toVersionComboBox)

        tranformButton = QtWidgets.QPushButton("&Transform", self)
        tranformButton.clicked.connect(self.accept)
        cancelButton = QtWidgets.QPushButton("&Cancel", self)
        cancelButton.clicked.connect(self.reject)

        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton(tranformButton, QtWidgets.QDialogButtonBox.AcceptRole)
        buttonBox.addButton(cancelButton, QtWidgets.QDialogButtonBox.RejectRole)

        mainVerticalLayout.addWidget(buttonBox)

        self.setMinimumSize(320, 200)

    def get_to_version(self):
        return self.toVersionComboBox.currentText()
