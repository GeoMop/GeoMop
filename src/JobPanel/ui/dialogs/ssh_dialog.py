# -*- coding: utf-8 -*-
"""
SSH dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets

#from helpers.importer import DialectImporter
from JobPanel.ui.data.preset_data import SshPreset
from JobPanel.ui.dialogs.dialogs import AFormContainer
from JobPanel.ui.validators.validation import PresetsValidationColorizer
from JobPanel.ui.dialogs.test_ssh_dialog import TestSSHDialog
from JobPanel.ui.dialogs import SshPasswordDialog
from JobPanel.ui.imports.workspaces_conf import BASE_DIR
import gm_base.config as config
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
        self.frontend_service = None

        # setup specific UI
        self.ui = UiSshDialog() 
        self.form = self.ui.setup_ui(parent, self)
        self.ui.validator.connect(self.valid)

        self.preset = None

        self.parent = parent

        self.ui.nameLineEdit.textChanged.connect(self.handle_data_changed)
        self.ui.hostLineEdit.textChanged.connect(self.handle_data_changed)
        self.ui.geomop_rootLineEdit.textChanged.connect(self.handle_data_changed)
        self.ui.workspaceLineEdit.textChanged.connect(self.handle_data_changed)
        self.ui.userLineEdit.textChanged.connect(self.handle_data_changed)
        self.ui.passwordLineEdit.textChanged.connect(self.handle_data_changed)
        self.ui.rememberPasswordCheckbox.stateChanged.connect(self.handle_data_changed)
        self.ui.pbsSystemComboBox.currentIndexChanged.connect(self.handle_data_changed)

        self.edit_enable(False)
       
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
            
        p = self.get_data()['preset']                
        if p.host!=self.preset.host:
            return True
        if p.port!=self.preset.port:
            return True
        if p.geomop_root!=self.preset.geomop_root:
            return True
        if p.workspace!=self.preset.workspace:
            return True
        if p.uid!=self.preset.uid:
            return True
        if self.preset.to_pc!=p.to_pc:
            return True
        # if self.preset.to_remote!=p.to_remote:
        #     return True
        # if self.preset.use_tunneling!=p.use_tunneling:
        #     return True
        # if self.preset.env != p.env:
        #     return True
        if self.preset.pbs_system!=p.pbs_system:
            return True
        # password
        if self.ui.passwordLineEdit.isEnabled():
            if self.preset.pwd != p.pwd:
                return True
        return False

    def get_data(self):
        name=self.ui.nameLineEdit.text()
        preset = SshPreset(name=name)

        # port separation
        text = self.ui.hostLineEdit.text()
        s = text.rsplit(":", 1)
        preset.host = s[0]
        if len(s) > 1:
            try:
                preset.port = int(s[1])
            except ValueError:
                preset.port = -1
        else:
            preset.port = 22

        preset.geomop_root = self.ui.geomop_rootLineEdit.text()
        preset.workspace = self.ui.workspaceLineEdit.text()
        preset.uid = self.ui.userLineEdit.text()
        preset.to_pc = self.ui.rememberPasswordCheckbox.isChecked()
        # preset.to_remote = (self.ui.copyPasswordCheckbox.isEnabled() and
        #                     self.ui.copyPasswordCheckbox.isChecked())
        #preset.use_tunneling = self.ui.useTunnelingCheckbox.isChecked()
        #preset.env = self.ui.envPresetComboBox.currentData()
        if self.ui.pbsSystemComboBox.currentText():
            preset.pbs_system = self.ui.pbsSystemComboBox.currentData()

        # password
        if self.ui.passwordLineEdit.isEnabled():
            preset.pwd = self.ui.passwordLineEdit.text()

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

            # host + port
            if preset.port != 22:
                host = "{}:{}".format(preset.host, preset.port)
            else:
                host = preset.host
            self.ui.hostLineEdit.setText(host)

            self.ui.geomop_rootLineEdit.setText(preset.geomop_root)
            self.ui.workspaceLineEdit.setText(preset.workspace)
            self.ui.userLineEdit.setText(preset.uid)
            self.ui.passwordLineEdit.setText(preset.pwd)
            self.ui.rememberPasswordCheckbox.setChecked(preset.to_pc)
            # self.ui.copyPasswordCheckbox.setChecked(preset.to_remote)
            # self.ui.useTunnelingCheckbox.setChecked(preset.use_tunneling)

            # todo: nevim jak lepe vyresit
            self.ui.pbsSystemComboBox.clear()
            self.ui.pbsSystemComboBox.addItem('No Pbs', '')
            dialect_items = {"PbsDialectPBSPro": "PBSPro"}
            for key in dialect_items:
                self.ui.pbsSystemComboBox.addItem(dialect_items[key], key)
            self.ui.pbsSystemComboBox.setCurrentIndex(
                self.ui.pbsSystemComboBox.findData(preset.pbs_system))

            # self.ui.envPresetComboBox.setCurrentIndex(
            #     self.ui.envPresetComboBox.findData(preset.env))
            self.valid()
        else:
            self.ui.nameLineEdit.setText("charon")
            self.ui.hostLineEdit.setText("charon.nti.tul.cz")
            self.ui.geomop_rootLineEdit.setText('/storage/liberec3-tul/home/radeksrb/geomop_1.1.0')
            self.ui.workspaceLineEdit.setText('workspace')
            self.ui.userLineEdit.clear()
            self.ui.passwordLineEdit.clear()
            self.ui.rememberPasswordCheckbox.setChecked(True)
            # self.ui.copyPasswordCheckbox.setChecked(True)
            # self.ui.useTunnelingCheckbox.setChecked(False)
            self.ui.pbsSystemComboBox.setCurrentIndex(0)

            # todo: nevim jak lepe vyresit
            self.ui.pbsSystemComboBox.clear()
            self.ui.pbsSystemComboBox.addItem('No Pbs', '')
            dialect_items = {"PbsDialectPBSPro": "PBSPro"}
            for key in dialect_items:
                self.ui.pbsSystemComboBox.addItem(dialect_items[key], key)
            self.ui.pbsSystemComboBox.setCurrentIndex(1)

            #self.ui.envPresetComboBox.setCurrentIndex(-1)
        self.update_test_labels()
        self.edit_enable(True)

    def edit_enable(self, enable=True):
        self.ui.nameLineEdit.setEnabled(enable)
        self.ui.hostLineEdit.setEnabled(enable)
        self.ui.geomop_rootLineEdit.setEnabled(enable)
        self.ui.workspaceLineEdit.setEnabled(enable)
        self.ui.userLineEdit.setEnabled(enable)
        self.ui.passwordLineEdit.setEnabled(enable)
        self.ui.rememberPasswordCheckbox.setEnabled(enable)
        self.ui.pbsSystemComboBox.setEnabled(enable)
        self.ui.btnTest.setEnabled(enable)

        if enable:
            self.ui._handle_remember_password_checkbox_changed()

    def set_data_container(self, data, frontend_service):
        self.data = data
        self.frontend_service = frontend_service
        # env = data.env_presets
        # self.ui.envPresetComboBox.clear()
        
        # self.permitted['env'] = []
        # if not env or len(env)==0:
        #     self.permitted['env'].append("")
        #     self.ui.envPresetComboBox.addItem('Please set any environment preset', '')
        self.permitted['pbs_system'] = []
        self.permitted['pbs_system'].append("")
        
        # if env:
        #     # sort dict by list, not sure how it works
        #     for key in env:
        #         self.ui.envPresetComboBox.addItem(env[key].name, key)
        #         self.permitted['env'].append(key)
        #     if self.preset is not None:
        #         self.ui.envPresetComboBox.setCurrentIndex(
        #             self.ui.envPresetComboBox.findData(self.preset.env))
                    
        #self.ui.pbsSystemComboBox.clear()
        #self.ui.pbsSystemComboBox.addItem('No Pbs', '')
        #dialect_items = DialectImporter.get_available_dialects()
        dialect_items = {"PbsDialectPBSPro": "PBSPro"}
        for key in dialect_items:
            #self.ui.pbsSystemComboBox.addItem(dialect_items[key], key)
            self.permitted['pbs_system'].append(key)
                
    def handle_test(self):
        """Do ssh connection test"""
        if self.is_dirty():
            if not self.parent._handle_save_preset_action():
                return

        preset = self.get_data()['preset']
        if not preset.to_pc:
            dialog = SshPasswordDialog(None, preset)
            if dialog.exec_():
                preset.pwd = dialog.password
            else:
                return
        else:
            preset.pwd = self.ui.passwordLineEdit.text()
        dialog = TestSSHDialog(self.parent, preset, self.frontend_service)
        dialog.exec_()
        if dialog.finished and (dialog.res_data is not None) and (not dialog.res_data["errors"]):
            self.parent.presets[preset.name].tested = True
            self.parent.presets[preset.name].home_dir = dialog.res_data["home_dir"]
            if "version" in dialog.res_data["installation_info"]:
                self.parent.presets[preset.name].geomop_version = dialog.res_data["installation_info"]["version"]
            else:
                self.parent.presets[preset.name].geomop_version = ""
            if "revision" in dialog.res_data["installation_info"]:
                self.parent.presets[preset.name].geomop_revision = dialog.res_data["installation_info"]["revision"]
            else:
                self.parent.presets[preset.name].geomop_revision = ""
            if "executables" in dialog.res_data["installation_info"]:
                self.parent.presets[preset.name].executables = \
                    [e["name"] for e in dialog.res_data["installation_info"]["executables"]]
            else:
                self.parent.presets[preset.name].executables = []
            self.parent.presets.save()
        else:
            self.parent.presets[preset.name].tested = False
            self.parent.presets[preset.name].home_dir = ""
            self.parent.presets[preset.name].executables = []
            self.parent.presets.save()
        self.update_test_labels()

    def handle_data_changed(self):
        self.update_test_labels()

    def update_test_labels(self):
        exec_text = "Available executables:\n"
        version_text = "GeoMop version: "
        revision_text = "GeoMop revision: "
        if self.parent.presets and (not self.is_dirty()) and self.preset.name in self.parent.presets and \
                self.parent.presets[self.preset.name].tested:
            self.ui.testedLabel.setText("The connection is tested.")
            self.ui.testedLabel.setStyleSheet("QLabel { color : green; }")
            version_text += self.parent.presets[self.preset.name].geomop_version
            revision_text += self.parent.presets[self.preset.name].geomop_revision[:10]
            exec_text += ", ".join(self.parent.presets[self.preset.name].executables)
        else:
            self.ui.testedLabel.setText("The connection must be tested before use.")
            self.ui.testedLabel.setStyleSheet("QLabel { color : red; }")
        self.ui.availableExecutablesLabel.setText(exec_text)
        self.ui.geomopVersionLabel.setText(version_text)
        self.ui.geomopRevisionLabel.setText(revision_text)


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
        self.validator.add('host', self.hostLineEdit)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.hostLineEdit)

        # # 3 row
        # self.portLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        # self.portLabel.setText("Specify port:")
        # self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
        #                           self.portLabel)
        # self.portSpinBox = QtWidgets.QSpinBox(
        #     self.mainVerticalLayoutWidget)
        # self.portSpinBox.setButtonSymbols(
        #     QtWidgets.QAbstractSpinBox.NoButtons)
        # self.portSpinBox.setMinimum(1)
        # self.portSpinBox.setValue(22)
        # self.portSpinBox.setMaximum(65535)
        # self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
        #                           self.portSpinBox)

        # 3 row
        self.geomop_rootLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.geomop_rootLabel.setText("GeoMop root directory:")
        self.geomop_rootLabel.setToolTip("Absolute path to GeoMop installation on the remote server.")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.geomop_rootLabel)
        self.geomop_rootLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.geomop_rootLineEdit.setText("")
        self.geomop_rootLineEdit.setProperty("clearButtonEnabled", True)
        self.validator.add('geomop_root',self.geomop_rootLineEdit)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.geomop_rootLineEdit)

        # 4 row
        self.workspaceLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.workspaceLabel.setText("Analysis workspace directory:")
        self.workspaceLabel.setToolTip("Absolute or relative (to user's home) path\n "
                                       "to the workspace on the remote server.")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.workspaceLabel)
        self.workspaceLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.workspaceLineEdit.setText("")
        self.workspaceLineEdit.setProperty("clearButtonEnabled", True)
        self.validator.add('workspace', self.workspaceLineEdit)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.workspaceLineEdit)

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
        #self.copyPasswordCheckbox = QtWidgets.QCheckBox()
        #self.copyPasswordCheckbox.setText('Copy password to remote')
        #self.useTunnelingCheckbox = QtWidgets.QCheckBox()
        #self.useTunnelingCheckbox.setText('Use ssh tunneling')
        #self.useTunnelingCheckbox.setEnabled(False)
        self.passwordLayout.addWidget(self.passwordLineEdit)
        self.passwordLayout.addWidget(self.rememberPasswordCheckbox)
        #self.passwordLayout.addWidget(self.copyPasswordCheckbox)
        #self.passwordLayout.addWidget(self.useTunnelingCheckbox)
        
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
        self.validator.add('pbs_system', self.pbsSystemComboBox)        
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.pbsSystemComboBox)

        # todo: nevim jak lepe vyresit
        self.pbsSystemComboBox.clear()
        self.pbsSystemComboBox.addItem('No Pbs', '')
        dialect_items = {"PbsDialectPBSPro": "PBSPro"}
        for key in dialect_items:
            self.pbsSystemComboBox.addItem(dialect_items[key], key)

        # # 9 row
        # self.envPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        # self.envPresetLabel.setText(self.ENV_LABEL)
        # self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole,
        #                            self.envPresetLabel)
        # self.envPresetComboBox = QtWidgets.QComboBox(
        #     self.mainVerticalLayoutWidget)
        # self.envPresetComboBox.setEnabled(False)
        # self.validator.add('env',  self.envPresetComboBox)
        # self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole,
        #                            self.envPresetComboBox)
                                   
        # 9 row
        self.btnTest = QtWidgets.QPushButton(dialog)
        self.btnTest.setText("Save and Test")
        #self.btnTest.setEnabled(False)
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole,
                                   self.btnTest)
                                   
        self.btnTest.clicked.connect(parent.handle_test)

        self.testedLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.testedLabel.setWordWrap(True)
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.testedLabel)

        self.geomopVersionLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole, self.geomopVersionLabel)

        self.geomopRevisionLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole, self.geomopRevisionLabel)

        self.availableExecutablesLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.availableExecutablesLabel.setWordWrap(True)
        self.formLayout.setWidget(13, QtWidgets.QFormLayout.LabelRole, self.availableExecutablesLabel)

        return self.formLayout

    def _handle_remember_password_checkbox_changed(self, state=None):
        if not self.rememberPasswordCheckbox.isChecked():
            #self.copyPasswordCheckbox.setChecked(False)
            #self.copyPasswordCheckbox.setEnabled(False)
            self.passwordLineEdit.setEnabled(False)
        else:
            #self.copyPasswordCheckbox.setEnabled(True)
            self.passwordLineEdit.setEnabled(True)            
