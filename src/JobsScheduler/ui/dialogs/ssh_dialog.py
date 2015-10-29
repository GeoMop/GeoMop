# -*- coding: utf-8 -*-
"""
SSH dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from ui.dialogs.dialogs import UiFormDialog, AFormDialog


class SshDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

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

    def __init__(self, parent=None, purpose=PURPOSE_ADD, data=None):
        super(SshDialog, self).__init__(parent)
        # setup specific UI
        self.ui = UiSshDialog()
        self.ui.setup_ui(self)

        # set purpose
        self.set_purpose(purpose, data)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super(SshDialog, self)._connect_slots()
        # specific slots
        self.ui.showPushButton.pressed.connect(
            lambda: self.ui.passwordLineEdit.setEchoMode(
                QtWidgets.QLineEdit.Normal))
        self.ui.showPushButton.released.connect(
            lambda: self.ui.passwordLineEdit.setEchoMode(
                QtWidgets.QLineEdit.Password))
        self.ui.sclEnableCheckBox.stateChanged.connect(
            lambda state: self.ui.sclEnableLineEdit.setDisabled(not state)
        )

    def get_data(self):
        return (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text(),
                ("ssh://" +
                 self.ui.userLineEdit.text() + "@" +
                 self.ui.hostLineEdit.text() + ":" +
                 str(self.ui.portSpinBox.value())),
                self.ui.hostLineEdit.text(),
                self.ui.portSpinBox.value(),
                self.ui.userLineEdit.text(),
                self.ui.passwordLineEdit.text(),
                self.ui.sclEnableLineEdit.text()
                if self.ui.sclEnableCheckBox.isChecked() else None)

    def set_data(self, data=None):
        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.hostLineEdit.setText(data[3])
            self.ui.portSpinBox.setValue(data[4])
            self.ui.userLineEdit.setText(data[5])
            self.ui.passwordLineEdit.setText(data[6])
            if data[7]:
                self.ui.sclEnableCheckBox.setCheckState(Qt.Checked)
                self.ui.sclEnableLineEdit.setText(data[7])
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.hostLineEdit.clear()
            self.ui.portSpinBox.setValue(22)
            self.ui.userLineEdit.clear()
            self.ui.passwordLineEdit.clear()
            self.ui.sclEnableCheckBox.setCheckState(Qt.Unchecked)
            self.ui.sclEnableLineEdit.clear()


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
        self.passwordRowSplit = QtWidgets.QHBoxLayout()
        self.passwordRowSplit.setObjectName("passwordRowSplit")
        self.passwordLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setPlaceholderText("User password")
        self.passwordLineEdit.setProperty("clearButtonEnabled", True)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordRowSplit.addWidget(self.passwordLineEdit)
        self.showPushButton = QtWidgets.QPushButton(
            self.mainVerticalLayoutWidget)
        self.showPushButton.setObjectName("showPushButton")
        self.showPushButton.setText("Show")
        self.passwordRowSplit.addWidget(self.showPushButton)
        self.formLayout.setLayout(5, QtWidgets.QFormLayout.FieldRole,
                                  self.passwordRowSplit)

        # 6 row
        self.sclEnableLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.sclEnableLabel.setObjectName("sclEnableLabel")
        self.sclEnableLabel.setText("SCL Enable:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.sclEnableLabel)
        self.sclEnableRowSplit = QtWidgets.QHBoxLayout()
        self.sclEnableRowSplit.setObjectName("sclEnableRowSplit")
        self.sclEnableLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.sclEnableLineEdit.setObjectName("sclEnableLineEdit")
        self.sclEnableLineEdit.setPlaceholderText("for example: python33")
        self.sclEnableLineEdit.setProperty("clearButtonEnabled", True)
        self.sclEnableLineEdit.setDisabled(True)
        self.sclEnableCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.showPushButton.setObjectName("sclEnableCheckBox")
        self.sclEnableRowSplit.addWidget(self.sclEnableCheckBox)
        self.sclEnableRowSplit.addWidget(self.sclEnableLineEdit)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole,
                                  self.sclEnableRowSplit)
