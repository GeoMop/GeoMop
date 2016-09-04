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
from ui.validators.validation import SshNameValidator, ValidationColorizer, RemoteDirectoryValidator
from data import Users
import config


class SshDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddSshDialog",
                       windowTitle="Job Panel - Add SSH host",
                       title="Add SSH host",
                       subtitle="Please select details for new SSH host.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditSshDialog",
                        windowTitle="Job Panel - Edit SSH host",
                        title="Edit SSH host",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopySshDialog",
                        windowTitle="Job Panel - Copy SSH host",
                        title="Copy SSH host",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, excluded_names=None):
        super().__init__(parent)
        self.excluded_names = excluded_names

        # setup specific UI
        self.ui = UiSshDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)

        self.preset = None

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
        name=self.ui.nameLineEdit.text()
        preset = SshPreset(name=name)
        preset.host = self.ui.hostLineEdit.text()
        preset.port = self.ui.portSpinBox.value()
        preset.remote_dir = self.ui.remoteDirLineEdit.text()
        preset.uid = self.ui.userLineEdit.text()
        preset.to_pc = self.ui.rememberPasswordCheckbox.isChecked()
        preset.to_remote = (self.ui.copyPasswordCheckbox.isEnabled() and
                            self.ui.copyPasswordCheckbox.isChecked())
        if self.ui.pbsSystemComboBox.currentText():
            preset.pbs_system = self.ui.pbsSystemComboBox.currentData()

        # password
        if self.ui.passwordLineEdit.isEnabled():
            password = self.ui.passwordLineEdit.text()
            if self.preset is None or password != self.preset.pwd:
                # if password changed
                key = Users.save_reg(name, password, config.__config_dir__)
                preset.pwd = "a124b.#"
                preset.key = key
            else:
                preset.pwd = self.preset.pwd
                preset.key = self.preset.key

        return {'preset': preset,
                'old_name': self.old_name}

    def set_data(self, data=None, is_edit=False):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)

        if data:
            preset = data['preset']
            self.preset = preset
            self.old_name = preset.name
            if is_edit:
                try:
                    self.excluded_names.remove(preset.name)
                except ValueError:
                    pass
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.hostLineEdit.setText(preset.host)
            self.ui.portSpinBox.setValue(preset.port)
            self.ui.remoteDirLineEdit.setText(preset.remote_dir)
            self.ui.userLineEdit.setText(preset.uid)
            pwd = Users.get_reg(preset.name, preset.key, config.__config_dir__)
            self.ui.passwordLineEdit.setText(pwd)
            self.ui.rememberPasswordCheckbox.setChecked(preset.to_pc)
            self.ui.copyPasswordCheckbox.setChecked(preset.to_remote)
            self.ui.pbsSystemComboBox.setCurrentIndex(
                self.ui.pbsSystemComboBox.findData(preset.pbs_system))
        else:
            self.ui.nameLineEdit.clear()
            self.ui.hostLineEdit.clear()
            self.ui.portSpinBox.setValue(22)
            self.ui.remoteDirLineEdit.setText('js_services')
            self.ui.userLineEdit.clear()
            self.ui.passwordLineEdit.clear()
            self.ui.rememberPasswordCheckbox.setChecked(True)
            self.ui.copyPasswordCheckbox.setChecked(True)
            self.ui.pbsSystemComboBox.setCurrentIndex(0)


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
            parent=self.mainVerticalLayoutWidget,
            excluded=dialog.excluded_names)
        self.remoteDirValidator = RemoteDirectoryValidator(
            parent=self.mainVerticalLayoutWidget
        )

        # form layout

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
        self.remoteDirLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.remoteDirLabel.setObjectName("remoteDirLabel")
        self.remoteDirLabel.setText("Remote directory:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.remoteDirLabel)
        self.remoteDirLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.remoteDirLineEdit.setObjectName("remoteDirLineEdit")
        self.remoteDirLineEdit.setText("js_services")
        self.remoteDirLineEdit.setValidator(self.remoteDirValidator)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.remoteDirLineEdit)

        # 5 row
        self.userLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.userLabel.setObjectName("userLabel")
        self.userLabel.setText("User:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.userLabel)
        self.userLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.userLineEdit.setObjectName("userLineEdit")
        self.userLineEdit.setPlaceholderText("User name")
        self.userLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.userLineEdit)

        # 6 row
        self.passwordLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.passwordLabel.setObjectName("passwordLabel")
        self.passwordLabel.setText("Password:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.passwordLabel)

        self.passwordLayout = QtWidgets.QVBoxLayout()
        self.passwordLineEdit = QtWidgets.QLineEdit()
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setPlaceholderText("User password")
        self.passwordLineEdit.setProperty("clearButtonEnabled", True)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.rememberPasswordCheckbox = QtWidgets.QCheckBox()
        self.rememberPasswordCheckbox.setText('Remember password')
        self.copyPasswordCheckbox = QtWidgets.QCheckBox()
        self.copyPasswordCheckbox.setText('Copy password to remote')
        self.passwordLayout.addWidget(self.passwordLineEdit)
        self.passwordLayout.addWidget(self.rememberPasswordCheckbox)
        self.passwordLayout.addWidget(self.copyPasswordCheckbox)
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole,
                                  self.passwordLayout)

        self.rememberPasswordCheckbox.stateChanged.connect(
            self._handle_remember_password_checkbox_changed)
        self._handle_remember_password_checkbox_changed()

        # 7 row
        self.pbsSystemLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.pbsSystemLabel.setObjectName("pbsSystemLabel")
        self.pbsSystemLabel.setText("PBS System:")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.pbsSystemLabel)
        self.pbsSystemComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.pbsSystemComboBox.setObjectName(
            "pbsSystemComboBox")
        self.pbsSystemComboBox.addItem('No Pbs', '')
        dialect_items = DialectImporter.get_available_dialects()
        for key in dialect_items:
            self.pbsSystemComboBox.addItem(dialect_items[key], key)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.pbsSystemComboBox)

        return dialog

    def _handle_remember_password_checkbox_changed(self, state=None):
        if not self.rememberPasswordCheckbox.isChecked():
            self.copyPasswordCheckbox.setChecked(False)
            self.copyPasswordCheckbox.setEnabled(False)
            self.passwordLineEdit.setEnabled(False)
        else:
            self.copyPasswordCheckbox.setEnabled(True)
            self.passwordLineEdit.setEnabled(True)
