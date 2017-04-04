# -*- coding: utf-8 -*-
"""
Env dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from ui.data.preset_data import EnvPreset
from ui.dialogs.dialogs import AFormContainer
from ui.validators.validation import PresetNameValidator, ValidationColorizer


class EnvDialog(AFormContainer):
    """
    Dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddEnvDialog",
                       windowTitle="Job Panel - Add Environment",
                       title="Add Environment",
                       subtitle="Please select details for new Environment.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditEnvDialog",
                        windowTitle="Job Panel - Edit Environment",
                        title="Edit Environment",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyEnvDialog",
                        windowTitle="Job Panel - Copy Environment",
                        title="Copy Environment",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent, excluded_names=None):
        super().__init__(parent)
        self.excluded_names = excluded_names
        self.data = None

        # setup specific UI
        self.ui = UiEnvDialog()
        self.form = self.ui.setup_ui(parent, self.excluded_names)

        self.preset = None
        self.ui.sclEnableCheckBox.stateChanged.connect(
            lambda state: self.ui.sclEnableLineEdit.setDisabled(not state)
        )
        self.ui.addModuleCheckBox.stateChanged.connect(
            lambda state: self.ui.addModuleLineEdit.setDisabled(not state)
        )

    def valid(self):
        valid = True
        if not ValidationColorizer.colorize_by_validator(
                self.ui.nameLineEdit):
            valid = False
        return valid
        
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
        if self.ui.sclEnableCheckBox.isChecked():
            if self.preset.scl_enable_exec!=self.ui.sclEnableLineEdit.text():
                return True
        else:
            if self.preset.scl_enable_exec is not None:
                return True
        if self.ui.addModuleCheckBox.isChecked():
            if self.preset.module_add!=self.ui.addModuleLineEdit.text():
                return True
        else:
            if self.preset.module_add is not None:
                return True
        if self.ui.flowPathEdit.text():
            if self.preset.flow_path!=self.ui.flowPathEdit.text():
                return True
        else:
            if self.preset.flow_path is not None:
                return True
        if self.ui.pbsParamsTextEdit.toPlainText():
            if self.preset.pbs_params!=self.ui.pbsParamsTextEdit.toPlainText().splitlines():
                return True
        else:
            if self.preset.pbs_params is not None and \
                len(self.preset.pbs_params)!=0:
                return True
        if self.ui.cliParamsTextEdit.toPlainText():
            if self.preset.cli_params!=self.ui.cliParamsTextEdit.toPlainText().splitlines():
                return True
        else:
            if self.preset.cli_params is not None and \
                len(self.preset.cli_params)!=0:
                return True
        return False

    def get_data(self):
        preset = EnvPreset(name=self.ui.nameLineEdit.text())
        if self.ui.pythonExecLineEdit.text():
            preset.python_exec = self.ui.pythonExecLineEdit.text()
        if self.ui.sclEnableCheckBox.isChecked():
            preset.scl_enable_exec = self.ui.sclEnableLineEdit.text()
        if self.ui.addModuleCheckBox.isChecked():
            preset.module_add = self.ui.addModuleLineEdit.text()
        if self.ui.flowPathEdit.text():
            preset.flow_path = self.ui.flowPathEdit.text()
        if self.ui.pbsParamsTextEdit.toPlainText():
            preset.pbs_params = self.ui.pbsParamsTextEdit.toPlainText().splitlines()
        if self.ui.cliParamsTextEdit.toPlainText():
            preset.cli_params = self.ui.cliParamsTextEdit.toPlainText().splitlines()
        return {
            'preset': preset,
            'old_name': self.old_name
        }

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
            self.ui.pythonExecLineEdit.setText(preset.python_exec)
            if preset.scl_enable_exec:
                self.ui.sclEnableCheckBox.setCheckState(Qt.Checked)
                self.ui.sclEnableLineEdit.setText(preset.scl_enable_exec)
            if preset.module_add:
                self.ui.addModuleCheckBox.setCheckState(Qt.Checked)
                self.ui.addModuleLineEdit.setText(preset.module_add)
            self.ui.flowPathEdit.setText(preset.flow_path)
            self.ui.pbsParamsTextEdit.setPlainText('\n'.join(preset.pbs_params))
            self.ui.cliParamsTextEdit.setPlainText('\n'.join(preset.cli_params))
        else:
            self.ui.nameLineEdit.clear()
            self.ui.pythonExecLineEdit.clear()
            self.ui.sclEnableCheckBox.setCheckState(Qt.Unchecked)
            self.ui.sclEnableLineEdit.clear()
            self.ui.addModuleCheckBox.setCheckState(Qt.Unchecked)
            self.ui.addModuleLineEdit.clear()
            self.ui.flowPathEdit.clear()
            self.ui.pbsParamsTextEdit.clear()
            self.ui.cliParamsTextEdit.clear()


class UiEnvDialog():
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog, excluded_names):

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.mainVerticalLayout = QtWidgets.QVBoxLayout()   
        self.mainVerticalLayout.setContentsMargins(10, 15, 10, 15)
        
        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout)

        # validators
        self.nameValidator = PresetNameValidator(
            parent=self.mainVerticalLayoutWidget,
            excluded=excluded_names)

        # form layout
        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setPlaceholderText("Name of the environment")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.nameLineEdit.setValidator(self.nameValidator)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # divider
        self.formDivider = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.formDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.formDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.formDivider)

        # font
        labelFont = QtGui.QFont()
        labelFont.setPointSize(11)
        labelFont.setWeight(65)

        # python label
        self.pythonLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.pythonLabel.setFont(labelFont)
        self.pythonLabel.setText("Python")
        self.mainVerticalLayout.addWidget(self.pythonLabel)

        # form layout2
        self.formLayout2 = QtWidgets.QFormLayout()
        self.formLayout2.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout2)

        # 1 row
        self.pythonExecLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.pythonExecLabel.setText("Interpreter:")
        self.formLayout2.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                   self.pythonExecLabel)
        self.pythonExecLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.pythonExecLineEdit.setPlaceholderText("for example: python3")
        self.pythonExecLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout2.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                   self.pythonExecLineEdit)

        # 2 row
        self.sclEnableLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.sclEnableLabel.setText("SCL Enable:")
        self.formLayout2.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.sclEnableLabel)
        self.sclEnableRowSplit = QtWidgets.QHBoxLayout()
        self.sclEnableLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.sclEnableLineEdit.setPlaceholderText("for example: python33")
        self.sclEnableLineEdit.setProperty("clearButtonEnabled", True)
        self.sclEnableLineEdit.setDisabled(True)
        self.sclEnableCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.sclEnableRowSplit.addWidget(self.sclEnableCheckBox)
        self.sclEnableRowSplit.addWidget(self.sclEnableLineEdit)
        self.formLayout2.setLayout(2, QtWidgets.QFormLayout.FieldRole,
                                   self.sclEnableRowSplit)

        # 3 row
        self.addModuleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.addModuleLabel.setText("Add module:")
        self.formLayout2.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                   self.addModuleLabel)
        self.addModuleRowSplit = QtWidgets.QHBoxLayout()
        self.addModuleLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.addModuleLineEdit.setPlaceholderText("for example: "
                                                  "python34-module-gcc")
        self.addModuleLineEdit.setProperty("clearButtonEnabled", True)
        self.addModuleLineEdit.setDisabled(True)
        self.addModuleCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.addModuleRowSplit.addWidget(self.addModuleCheckBox)
        self.addModuleRowSplit.addWidget(self.addModuleLineEdit)
        self.formLayout2.setLayout(3, QtWidgets.QFormLayout.FieldRole,
                                   self.addModuleRowSplit)

        # divider
        self.formDivider1 = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.formDivider1.setFrameShape(QtWidgets.QFrame.HLine)
        self.formDivider1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.formDivider1)

        # flow label
        self.flowLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.flowLabel.setFont(labelFont)
        self.flowLabel.setText("Flow123d")
        self.mainVerticalLayout.addWidget(self.flowLabel)

        # form layout3
        self.formLayout3 = QtWidgets.QFormLayout()
        self.formLayout3.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout3)

        # 1 row
        self.flowPathLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.flowPathLabel.setText("Flow123d path:")
        self.formLayout3.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                   self.flowPathLabel)
        self.flowPathEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.flowPathEdit.setPlaceholderText("flow123d")
        #self.flowPathEdit.setProperty("clearButtonEnabled", True)
        self.formLayout3.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                   self.flowPathEdit)

        # 2 row
        self.pbsParamsLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.pbsParamsLabel.setText("PBS Params:")
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.pbsParamsLabel)
        self.pbsParamsTextEdit = QtWidgets.QPlainTextEdit(
            self.mainVerticalLayoutWidget)
        self.pbsParamsTextEdit.setMinimumHeight(55)
        self.pbsParamsTextEdit.setTabChangesFocus(True)
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                   self.pbsParamsTextEdit)

        # 3 row
        self.cliParamsLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.cliParamsLabel.setText("CLI Params:")
        self.formLayout3.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                   self.cliParamsLabel)
        self.cliParamsTextEdit = QtWidgets.QPlainTextEdit(
            self.mainVerticalLayoutWidget)
        self.cliParamsTextEdit.setMinimumHeight(55)
        self.cliParamsTextEdit.setTabChangesFocus(True)
        self.formLayout3.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                   self.cliParamsTextEdit)
        
        return self.mainVerticalLayout
