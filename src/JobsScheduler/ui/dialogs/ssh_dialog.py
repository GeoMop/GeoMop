# -*- coding: utf-8 -*-
"""
MultiJob dialogs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets

from ui.dialogs.dialogs import UiFormDialog


class SshDialog(QtWidgets.QDialog):
    """
    Dialog executive code with bindings and other functionality.
    """
    # Dialog purpose
    purpose = None

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddSshDialog",
                       windowTitle="Job Scheduler - Add new SSH Preset",
                       title="Add new SSH Preset",
                       subtitle="Please select details for new SSH preset.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditSshDialog",
                        windowTitle="Job Scheduler - Edit SSH Preset",
                        title="Edit SSH Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopySshDialog",
                        windowTitle="Job Scheduler - Copy SSH Preset",
                        title="Copy SSH Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    # Overwrite with custom accept
    accepted = QtCore.pyqtSignal(dict, list)

    def __init__(self, parent=None, purpose=PURPOSE_ADD, data=None):
        super(SshDialog, self).__init__(parent)
        self.ui = UiSshDialog()
        self.ui.setup_ui(self)
        self.set_purpose(purpose, data)

        # connect slots
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def accept(self):
        super(SshDialog, self).accept()
        self.accepted.emit(self.purpose, self.get_data())

    def set_purpose(self, purpose=None, data=None):
        self.set_data(data)
        self.purpose = purpose
        self.setObjectName(purpose["objectName"])
        self.setWindowTitle(purpose["windowTitle"])
        self.ui.titleLabel.setText(purpose["title"])
        self.ui.subtitleLabel.setText(purpose["subtitle"])

    def get_data(self):
        data = list()
        data.append(self.ui.idLineEdit.text())
        data.append(self.ui.nameLineEdit.text())
        data.append(self.ui.hostLineEdit.text())
        data.append(self.ui.portSpinBox.value())
        data.append(self.ui.userLineEdit.text())
        data.append(self.ui.passwordLineEdit.text())
        return data

    def set_data(self, data=None):
        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.hostLineEdit.setText(data[2])
            self.ui.portSpinBox.setValue(data[3])
            self.ui.userLineEdit.setText(data[4])
            self.ui.passwordLineEdit.setText(data[5])
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.hostLineEdit.clear()
            self.ui.portSpinBox.setValue(22)
            self.ui.userLineEdit.clear()
            self.ui.passwordLineEdit.clear()


class UiSshDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        # form layout
        # hidden row
        self.idLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.idLabel.setObjectName("idLabel")
        self.idLabel.setText("Id:")
        self.idLabel.setVisible(False)
        # self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole,
        #                         self.idLabel)
        self.idLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.idLineEdit.setObjectName("idLineEdit")
        self.idLineEdit.setPlaceholderText("This should be hidden")
        self.idLineEdit.setVisible(False)
        # self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole,
        #                          self.idLineEdit)

        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setPlaceholderText("Name of the preset")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # 2 row
        self.hostLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.hostLabel.setObjectName("hostLabel")
        self.hostLabel.setText("Host:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.hostLabel)
        self.hostLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.hostLineEdit.setObjectName("hostLineEdit")
        self.hostLineEdit.setPlaceholderText("Insert valid host address")
        self.hostLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.hostLineEdit)

        # 3 row
        self.portLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.portLabel.setObjectName("portLabel")
        self.portLabel.setText("Specify port:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.portLabel)
        self.portSpinBox = QtWidgets.QSpinBox(
            self.mainVerticalLayoutWidget)
        self.portSpinBox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.NoButtons)
        self.portSpinBox.setMinimum(1)
        self.portSpinBox.setValue(22)
        self.portSpinBox.setMaximum(65535)
        self.portSpinBox.setObjectName("portSpinBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.portSpinBox)

        # 4 row
        self.userLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.userLabel.setObjectName("userLabel")
        self.userLabel.setText("User:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.userLabel)
        self.userLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.userLineEdit.setObjectName("userLineEdit")
        self.userLineEdit.setPlaceholderText("User name")
        self.userLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.userLineEdit)

        # 5 row
        self.passwordLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.passwordLabel.setObjectName("passwordLabel")
        self.passwordLabel.setText("Password:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.passwordLabel)
        self.passwordLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setPlaceholderText("User password")
        self.passwordLineEdit.setProperty("clearButtonEnabled", True)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.passwordLineEdit)
