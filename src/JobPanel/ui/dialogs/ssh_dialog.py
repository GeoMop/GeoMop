# -*- coding: utf-8 -*-
"""
SSH dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets

from helpers.importer import DialectImporter
from ui.data.preset_data import SshPreset
from ui.dialogs.dialogs import AFormContainer
from ui.validators.validation import PresetsValidationColorizer
from ui.dialogs.test_ssh_dialog import TestSSHDialog
from data import Users
from ui.dialogs import SshPasswordDialog
from ui.imports.workspaces_conf import BASE_DIR
import config
import os

class SshDialog(AFormContainer):
    """
    Dialog executive code with bindings and other functionality.
    """
    def __init__(self, parent, excluded_names=None):
        super().__init__(parent)
        
        self.excluded = {}
        self.excluded["name"]=excluded_names
        self.permitted = {}
        self.data = None

        # setup specific UI
        self.ui = UiSshDialog() 
        self.form = self.ui.setup_ui(parent, self)
        self.ui.validator.connect(self.valid)

        self.preset = None
       
    def first_focus(self):
        """
        Get focus to first property
        """
        self.ui.nameLineEdit.setFocus()
        
    def is_dirty(self):        
        """return if data was changes"""
        if self.preset is None:
            return True
        if self.old_name!=self.ui.nameLineEdit.text():
            return True            
        if self.ui.hostLineEdit.text()!=self.preset.host:
            return True
        if self.ui.portSpinBox.value()!=self.preset.port:
            return True
        if self.ui.remoteDirLineEdit.text()!=self.preset.remote_dir:
            return True
        if self.ui.userLineEdit.text()!=self.preset.uid:
            return True
        if self.preset.to_pc!=self.ui.rememberPasswordCheckbox.isChecked():
            return True
        to_remote = (self.ui.copyPasswordCheckbox.isEnabled() and
                            self.ui.copyPasswordCheckbox.isChecked())                            
        if self.preset.to_remote!=to_remote:
            return True
        if self.preset.use_tunneling!=self.ui.useTunnelingCheckbox.isChecked():
            return True
        if self.preset.env != self.ui.envPresetComboBox.currentData():
            return True
        if self.ui.pbsSystemComboBox.currentText():
            if self.preset.pbs_system!=self.ui.pbsSystemComboBox.currentData():
                return True
        # password
        if self.ui.passwordLineEdit.isEnabled():
            password = self.ui.passwordLineEdit.text()
            pwd2 = Users.get_reg(self.preset.name, self.preset.key, os.path.join(
                config.__config_dir__, BASE_DIR))
            if password != pwd2:
                return True
        return False

    def get_data(self, save_reg=True):
        name=self.ui.nameLineEdit.text()
        preset = SshPreset(name=name)
        preset.host = self.ui.hostLineEdit.text()
        preset.port = self.ui.portSpinBox.value()
        preset.remote_dir = self.ui.remoteDirLineEdit.text()
        preset.uid = self.ui.userLineEdit.text()
        preset.to_pc = self.ui.rememberPasswordCheckbox.isChecked()
        preset.to_remote = (self.ui.copyPasswordCheckbox.isEnabled() and
                            self.ui.copyPasswordCheckbox.isChecked())
        preset.use_tunneling = self.ui.useTunnelingCheckbox.isChecked()
        preset.env = self.ui.envPresetComboBox.currentData()
        if self.ui.pbsSystemComboBox.currentText():
            preset.pbs_system = self.ui.pbsSystemComboBox.currentData()

        # password
        if self.ui.passwordLineEdit.isEnabled():
            password = self.ui.passwordLineEdit.text()
            if save_reg:                
                if self.preset is None or password != self.preset.pwd:
                    # if password changed
                    key = Users.save_reg(name, password,
                        os.path.join(config.__config_dir__, BASE_DIR))
                    preset.pwd = "a124b.#"
                    preset.key = key
                else:
                    preset.pwd = self.preset.pwd
                    preset.key = self.preset.key

        return {'preset': preset,
                'old_name': self.old_name}

    def set_data(self, data=None, is_edit=False):
        # reset validation colors
        self.ui.validator.reset_colorize()

        if data:
            preset = data['preset']
            self.preset = preset
            self.old_name = preset.name
            if is_edit:
                try:
                    self.excluded["name"].remove(preset.name)
                except ValueError:
                    pass
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.hostLineEdit.setText(preset.host)
            self.ui.portSpinBox.setValue(preset.port)
            self.ui.remoteDirLineEdit.setText(preset.remote_dir)
            self.ui.userLineEdit.setText(preset.uid)
            pwd = Users.get_reg(preset.name, preset.key, 
                os.path.join(config.__config_dir__, BASE_DIR))
            if pwd is not None:
                self.ui.passwordLineEdit.setText(pwd)
                self.ui.rememberPasswordCheckbox.setChecked(preset.to_pc)
            else:
                self.ui.passwordLineEdit.setText("")
                self.ui.rememberPasswordCheckbox.setChecked(False)
            self.ui.copyPasswordCheckbox.setChecked(preset.to_remote)
            self.ui.useTunnelingCheckbox.setChecked(preset.use_tunneling)
            self.ui.pbsSystemComboBox.setCurrentIndex(
                self.ui.pbsSystemComboBox.findData(preset.pbs_system))
            self.ui.envPresetComboBox.setCurrentIndex(
                self.ui.envPresetComboBox.findData(preset.env))
            self.valid()
        else:
            self.ui.nameLineEdit.clear()
            self.ui.hostLineEdit.clear()
            self.ui.portSpinBox.setValue(22)
            self.ui.remoteDirLineEdit.setText('js_services')
            self.ui.userLineEdit.clear()
            self.ui.passwordLineEdit.clear()
            self.ui.rememberPasswordCheckbox.setChecked(True)
            self.ui.copyPasswordCheckbox.setChecked(True)
            self.ui.useTunnelingCheckbox.setChecked(False)
            self.ui.pbsSystemComboBox.setCurrentIndex(0)
            self.ui.envPresetComboBox.setCurrentIndex(-1)
        return 
            
    def set_data_container(self, data):
        self.data = data
        env = data.env_presets
        self.ui.envPresetComboBox.clear()
        if env:
            # sort dict by list, not sure how it works
            for key in env:
                self.ui.envPresetComboBox.addItem(env[key].name, key)
            if self.preset is not None:
                self.ui.envPresetComboBox.setCurrentIndex(
                    self.ui.envPresetComboBox.findData(self.preset.env))
                
    def handle_test(self):
        """Do ssh connection test"""
        preset = self.get_data(False)['preset']
        if not preset.to_pc:
            dialog = SshPasswordDialog(None, preset)
            if dialog.exec_():
                preset.pwd = dialog.password
            else:
                return
        else:
            preset.pwd = self.ui.passwordLineEdit.text()
        dialog = TestSSHDialog(self, preset, self.data)
        dialog.exec_()


class UiSshDialog():
    """
    UI extensions of form dialog.
    """
    ENV_LABEL = "Remote environment:"

    def setup_ui(self, dialog, parent):

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        
        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(10, 15, 10, 15)

        # validators
        self.validator = PresetsValidationColorizer()

        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setPlaceholderText("Name of the host")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.validator.add('name',self.nameLineEdit)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # 2 row
        self.hostLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.hostLabel.setText("Host:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.hostLabel)
        self.hostLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.hostLineEdit.setPlaceholderText("Valid host address or Ip")
        self.hostLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.hostLineEdit)

        # 3 row
        self.portLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
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
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.portSpinBox)

        # 4 row
        self.remoteDirLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.remoteDirLabel.setText("Remote directory:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.remoteDirLabel)
        self.remoteDirLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.remoteDirLineEdit.setText("js_services")
        self.validator.add('remote_dir',self.remoteDirLineEdit)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.remoteDirLineEdit)

        # 5 row
        self.userLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.userLabel.setText("User:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.userLabel)
        self.userLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.userLineEdit.setPlaceholderText("User name")
        self.userLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.userLineEdit)

        # 6 row
        self.passwordLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.passwordLabel.setText("Password:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.passwordLabel)

        self.passwordLayout = QtWidgets.QVBoxLayout()
        self.passwordLineEdit = QtWidgets.QLineEdit()
        self.passwordLineEdit.setPlaceholderText("User password")
        self.passwordLineEdit.setProperty("clearButtonEnabled", True)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.rememberPasswordCheckbox = QtWidgets.QCheckBox()
        self.rememberPasswordCheckbox.setText('Remember password')
        self.copyPasswordCheckbox = QtWidgets.QCheckBox()
        self.copyPasswordCheckbox.setText('Copy password to remote')        
        self.useTunnelingCheckbox = QtWidgets.QCheckBox()
        self.useTunnelingCheckbox.setText('Use ssh tunneling')        
        self.passwordLayout.addWidget(self.passwordLineEdit)
        self.passwordLayout.addWidget(self.rememberPasswordCheckbox)
        self.passwordLayout.addWidget(self.copyPasswordCheckbox)
        self.passwordLayout.addWidget(self.useTunnelingCheckbox)
        
        self.formLayout.setLayout(6, QtWidgets.QFormLayout.FieldRole,
                                  self.passwordLayout)

        self.rememberPasswordCheckbox.stateChanged.connect(
            self._handle_remember_password_checkbox_changed)
        self._handle_remember_password_checkbox_changed()

        # 7 row
        self.pbsSystemLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.pbsSystemLabel.setText("PBS System:")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.pbsSystemLabel)
        self.pbsSystemComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.pbsSystemComboBox.addItem('No Pbs', '')
        dialect_items = DialectImporter.get_available_dialects()
        for key in dialect_items:
            self.pbsSystemComboBox.addItem(dialect_items[key], key)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.pbsSystemComboBox)
                                  
        # 8 row
        self.envPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.envPresetLabel.setText(self.ENV_LABEL)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole,
                                   self.envPresetLabel)
        self.envPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole,
                                   self.envPresetComboBox)
                                   
        # 9 row
        self.btnTest = QtWidgets.QPushButton(dialog)
        self.btnTest.setText("Test Connection")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole,
                                   self.btnTest)
                                   
        self.btnTest.clicked.connect(parent.handle_test)

        return self.formLayout

    def _handle_remember_password_checkbox_changed(self, state=None):
        if not self.rememberPasswordCheckbox.isChecked():
            self.copyPasswordCheckbox.setChecked(False)
            self.copyPasswordCheckbox.setEnabled(False)
            self.passwordLineEdit.setEnabled(False)
        else:
            self.copyPasswordCheckbox.setEnabled(True)
            self.passwordLineEdit.setEnabled(True)            
