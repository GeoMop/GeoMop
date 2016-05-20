# -*- coding: utf-8 -*-
"""
SSH dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets

from helpers.importer import DialectImporter
from ui.data.preset_data import SshPreset
from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import SshNameValidator, ValidationColorizer


class SshDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddSshDialog",
                       windowTitle="Job Scheduler - Add SSH host",
                       title="Add SSH host",
                       subtitle="Please select details for new SSH host.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditSshDialog",
                        windowTitle="Job Scheduler - Edit SSH host",
                        title="Edit SSH host",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopySshDialog",
                        windowTitle="Job Scheduler - Copy SSH host",
                        title="Copy SSH host",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None):
        super().__init__(parent)
        # setup specific UI
        self.ui = UiSshDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super()._connect_slots()

    def valid(self):
        valid = True
        if not ValidationColorizer.colorize_by_validator(
                self.ui.nameLineEdit):
            valid = False
        return valid

    def get_data(self):
        key = self.ui.idLineEdit.text()
        preset = SshPreset(name=self.ui.nameLineEdit.text())
        preset.host = self.ui.hostLineEdit.text()
        preset.port = self.ui.portSpinBox.value()
        preset.uid = self.ui.userLineEdit.text()
        preset.pwd = self.ui.passwordLineEdit.text()
        if self.ui.pbsSystemComboBox.currentText():
            preset.pbs_system = self.ui.pbsSystemComboBox.currentData()
        return {
            "key": key,
            "preset": preset
        }

    def set_data(self, data=None):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)

        if data:
            key = data["key"]
            preset = data["preset"]
            self.ui.idLineEdit.setText(key)
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.hostLineEdit.setText(preset.host)
            self.ui.portSpinBox.setValue(preset.port)
            self.ui.userLineEdit.setText(preset.uid)
            self.ui.passwordLineEdit.setText(preset.pwd)
            self.ui.pbsSystemComboBox.setCurrentIndex(
                self.ui.pbsSystemComboBox.findData(preset.pbs_system))
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.hostLineEdit.clear()
            self.ui.portSpinBox.setValue(22)
            self.ui.userLineEdit.clear()
            self.ui.passwordLineEdit.clear()
            self.ui.pbsSystemComboBox.setCurrentIndex(-1)


class UiSshDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        # validators
        self.nameValidator = SshNameValidator(
            parent=self.mainVerticalLayoutWidget)

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
        self.nameLineEdit.setPlaceholderText("Name of the host")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.nameLineEdit.setValidator(self.nameValidator)
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
        self.hostLineEdit.setPlaceholderText("Valid host address or Ip")
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

        # 6 row
        self.pbsSystemLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.pbsSystemLabel.setObjectName("pbsSystemLabel")
        self.pbsSystemLabel.setText("PBS System:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.pbsSystemLabel)
        self.pbsSystemComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.pbsSystemComboBox.setObjectName(
            "pbsSystemComboBox")
        self.pbsSystemComboBox.addItem("")
        dialect_items = DialectImporter.get_available_dialects()
        for key in dialect_items:
            self.pbsSystemComboBox.addItem(dialect_items[key], key)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.pbsSystemComboBox)

        return dialog
