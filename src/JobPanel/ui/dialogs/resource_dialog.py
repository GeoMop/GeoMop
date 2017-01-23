# -*- coding: utf-8 -*-
"""
Resource dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtGui, QtWidgets, QtCore

from ui.data.preset_data import ResPreset
from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import PresetNameValidator, ValidationColorizer


class ResourceDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddResourcehDialog",
                       windowTitle="Job Panel - Add Resource",
                       title="Add Resource",
                       subtitle="Please select details for new Resource.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditResourceDialog",
                        windowTitle="Job Panel - Edit Resource",
                        title="Edit Resource",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyResourceDialog",
                        windowTitle="Job Panel - Copy Resource",
                        title="Copy Resource",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, excluded_names=None):
        super().__init__(parent)
        self.excluded_names = excluded_names

        # setup specific UI
        self.ui = UiResourceDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)

        self.ssh = {}

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super()._connect_slots()
        # specific slots
        self.ui.multiJobSshPresetComboBox.currentIndexChanged.connect(
            self._handle_mj_ssh_changed)
        self.ui.jobSshPresetComboBox.currentIndexChanged.connect(
            self._handle_j_ssh_changed)

    def _handle_mj_ssh_changed(self, index):
        key = self.ui.multiJobSshPresetComboBox.currentText()
        if key == -1 or key == UiResourceDialog.SSH_LOCAL_EXEC or self.ssh[key].pbs_system == '':
            self.ui.multiJobPbsPresetComboBox.setEnabled(False)
        else:
            self._enable_pbs(self.ui.multiJobPbsPresetComboBox, key)
            
    def _enable_pbs(self, combo, key):
        """Enable all pbs presets with same sytems as is in choosed ssh preset"""
        combo.setEnabled(True)            
        model = combo.model()
        if not key in self.ssh:
            system = ''
        else:
            system = self.ssh[key].pbs_system
        reselect = False
        curr = combo.currentIndex()
        for i in range(0, combo.count()):
            item = model.item(i)
            if not item.text() in self.pbs:
                continue
            pbs_system = self.pbs[item.text()].pbs_system
            disable = pbs_system is None or system != pbs_system                
            if disable:
                item.setFlags(item.flags() & ~(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled))
                item.setData(combo.palette().color(
                    QtGui.QPalette.Disabled, QtGui.QPalette.Text), QtCore.Qt.TextColorRole)
                if curr == i:
                    reselect = True
            else:
                item.setFlags( item.flags()|QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsEnabled);
                item.setData(QtCore.QVariant(), QtCore.Qt.TextColorRole)
        if reselect:
            combo.setCurrentIndex(0)

    def _handle_j_ssh_changed(self, index):
        key = self.ui.jobSshPresetComboBox.currentText()
        if key in self.ssh and self.ssh[key].pbs_system == '':
            self.ui.jobPbsPresetComboBox.setEnabled(False)
        else:
            self._enable_pbs(self.ui.jobPbsPresetComboBox, key)

    def valid(self):
        valid = True
        if not ValidationColorizer.colorize_by_validator(
                self.ui.nameLineEdit):
            valid = False
        return valid

    def accept(self):
        if self.ui.nameLineEdit.text() == "":
            self.ui.nameLineEdit.setText(self.ui.multiJobSshPresetComboBox.currentText() + " " + \
                self.ui.multiJobPbsPresetComboBox.currentText())
        return super(ResourceDialog, self).accept()

    def set_pbs_presets(self, pbs):
        self.ui.multiJobPbsPresetComboBox.clear()
        self.ui.jobPbsPresetComboBox.clear()

        # add default PBS options (none)
        self.ui.multiJobPbsPresetComboBox.addItem(self.ui.PBS_OPTION_NONE, self.ui.PBS_OPTION_NONE)
        self.ui.jobPbsPresetComboBox.addItem(self.ui.PBS_OPTION_NONE, self.ui.PBS_OPTION_NONE)
        
        self.pbs = pbs

        if pbs:
            # sort dict by list, not sure how it works
            for key in pbs:
                self.ui.multiJobPbsPresetComboBox.addItem(pbs[key].name, key)
                self.ui.jobPbsPresetComboBox.addItem(pbs[key].name, key)

        self.ui.multiJobPbsPresetComboBox.setCurrentIndex(0)

    def set_ssh_presets(self, ssh):
        self.ui.multiJobSshPresetComboBox.clear()
        self.ui.jobSshPresetComboBox.clear()

        # add default SSH option for local execution
        self.ui.multiJobSshPresetComboBox.addItem(self.ui.SSH_LOCAL_EXEC, self.ui.SSH_LOCAL_EXEC)
        self.ui.jobSshPresetComboBox.addItem(self.ui.SSH_LOCAL_EXEC, self.ui.SSH_LOCAL_EXEC)

        self.ssh = ssh

        if ssh:
            # sort dict by list, not sure how it works
            for key in ssh:
                self.ui.multiJobSshPresetComboBox.addItem(ssh[key].name, key)
                self.ui.jobSshPresetComboBox.addItem(ssh[key].name, key)

    def get_data(self):
        preset = ResPreset(name=self.ui.nameLineEdit.text())

        if self.ui.multiJobSshPresetComboBox.currentText() != UiResourceDialog.SSH_LOCAL_EXEC:
            preset.mj_ssh_preset = self.ui.multiJobSshPresetComboBox.currentData()
        preset.mj_execution_type = UiResourceDialog.DELEGATOR_LABEL
        if self.ui.multiJobSshPresetComboBox.currentText() == UiResourceDialog.SSH_LOCAL_EXEC:
            preset.mj_execution_type = UiResourceDialog.EXEC_LABEL
        elif self.ui.multiJobPbsPresetComboBox.currentText() == UiResourceDialog.PBS_OPTION_NONE:
            preset.mj_remote_execution_type = UiResourceDialog.EXEC_LABEL
        else:
            preset.mj_remote_execution_type = UiResourceDialog.PBS_LABEL
        if self.ui.multiJobPbsPresetComboBox.isEnabled() and \
                self.ui.multiJobPbsPresetComboBox.currentIndex() != 0:
            preset.mj_pbs_preset =\
                self.ui.multiJobPbsPresetComboBox.currentData()        

        if self.ui.jobSshPresetComboBox.currentText() != UiResourceDialog.SSH_LOCAL_EXEC:
            preset.j_ssh_preset = self.ui.jobSshPresetComboBox.currentData()

        preset.j_execution_type = UiResourceDialog.REMOTE_LABEL
        if self.ui.jobSshPresetComboBox.currentText() == UiResourceDialog.SSH_LOCAL_EXEC:
            if self.ui.jobPbsPresetComboBox.currentText() == UiResourceDialog.PBS_OPTION_NONE:
                preset.j_execution_type = UiResourceDialog.EXEC_LABEL
            else:
                preset.j_execution_type = UiResourceDialog.PBS_LABEL
        elif self.ui.jobPbsPresetComboBox.currentText() == UiResourceDialog.PBS_OPTION_NONE:
            preset.j_remote_execution_type = UiResourceDialog.EXEC_LABEL
        else:
            preset.j_remote_execution_type = UiResourceDialog.PBS_LABEL

        if self.ui.jobPbsPresetComboBox.isEnabled() and \
                self.ui.jobPbsPresetComboBox.currentIndex() != 0:
            preset.j_pbs_preset = self.ui.jobPbsPresetComboBox.currentData()

        return {
            'preset': preset,
            'old_name': self.old_name
        }

    def set_data(self, data=None, is_edit=False):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)

        if data:
            preset = data["preset"]
            self.old_name = preset.name
            if is_edit:
                try:
                    self.excluded_names.remove(preset.name)
                except ValueError:
                    pass
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(
                self.ui.multiJobSshPresetComboBox.findData(
                    'local' if preset.mj_ssh_preset is None else preset.mj_ssh_preset))
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(
                self.ui.multiJobPbsPresetComboBox.findData(
                    'no PBS' if preset.mj_pbs_preset is None else preset.mj_pbs_preset))            

            self.ui.jobSshPresetComboBox.setCurrentIndex(
                self.ui.jobSshPresetComboBox.findData(
                    'local' if preset.j_ssh_preset is None else preset.j_ssh_preset))
            self.ui.jobPbsPresetComboBox.setCurrentIndex(
                self.ui.jobPbsPresetComboBox.findData(
                    'no PBS' if preset.j_pbs_preset is None else preset.j_pbs_preset)) 
        else:
            self.ui.nameLineEdit.clear()
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(0)
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(0)

            self.ui.jobPbsPresetComboBox.setCurrentIndex(0)


class UiResourceDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """
    EXECUTE_USING_LABEL = "Execute using:"
    EXECUTION_TYPE_LABEL = "Execution type:"
    SSH_PRESET_LABEL = "SSH host:"
    PBS_PRESET_LABEL = "PBS options:"    
    JOB_ENV_LABEL = "Job environment:"

    EXEC_LABEL = "EXEC"
    DELEGATOR_LABEL = "DELEGATOR"
    REMOTE_LABEL = "REMOTE"
    PBS_LABEL = "PBS"
    SSH_LOCAL_EXEC = "local"
    PBS_OPTION_NONE = "no PBS"

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        # validators
        self.nameValidator = PresetNameValidator(
            parent=self.mainVerticalLayoutWidget,
            excluded=dialog.excluded_names)

        # form layout
        # hidden row
        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setPlaceholderText("Name of the resource")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.nameLineEdit.setValidator(self.nameValidator)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # remove button box
        self.mainVerticalLayout.removeWidget(self.buttonBox)

        # divider
        self.formDivider = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.formDivider.setObjectName("formDivider")
        self.formDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.formDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.formDivider)

        # font
        labelFont = QtGui.QFont()
        labelFont.setPointSize(11)
        labelFont.setWeight(65)

        # multijob label
        self.multiJobLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.multiJobLabel.setObjectName("multijobLabel")
        self.multiJobLabel.setFont(labelFont)
        self.multiJobLabel.setText("MultiJob services")
        self.mainVerticalLayout.addWidget(self.multiJobLabel)

        # form layout2
        self.formLayout2 = QtWidgets.QFormLayout()
        self.formLayout2.setObjectName("formLayout2")
        self.formLayout2.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout2)

        # 1 row
        self.multiJobSshPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobSshPresetLabel.setObjectName("multiJobSshPresetLabel")
        self.multiJobSshPresetLabel.setText(self.SSH_PRESET_LABEL)
        self.formLayout2.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                   self.multiJobSshPresetLabel)
        self.multiJobSshPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobSshPresetComboBox.setObjectName(
            "multiJobSshPresetComboBox")
        self.formLayout2.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                   self.multiJobSshPresetComboBox)

        # 2 row
        self.multiJobPbsPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetLabel.setObjectName("multiJobPbsPresetLabel")
        self.multiJobPbsPresetLabel.setText(self.PBS_PRESET_LABEL)
        self.formLayout2.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.multiJobPbsPresetLabel)
        self.multiJobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetComboBox.setObjectName(
            "multiJobPbsPresetComboBox")
        self.formLayout2.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                   self.multiJobPbsPresetComboBox)

        # divider
        self.formDivider1 = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.formDivider1.setObjectName("formDivider")
        self.formDivider1.setFrameShape(QtWidgets.QFrame.HLine)
        self.formDivider1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.formDivider1)

        # job label
        self.jobLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.jobLabel.setObjectName("jobLabel")
        self.jobLabel.setFont(labelFont)
        self.jobLabel.setText("Job")
        self.mainVerticalLayout.addWidget(self.jobLabel)

        # form layout3
        self.mainVerticalLayout.removeWidget(self.buttonBox)
        self.formLayout3 = QtWidgets.QFormLayout()
        self.formLayout3.setObjectName("formLayout3")
        self.formLayout3.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout3)

        # 1 row
        self.jobSshPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobSshPresetLabel.setObjectName("jobSshPresetLabel")
        self.jobSshPresetLabel.setText(self.SSH_PRESET_LABEL)
        self.formLayout3.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                   self.jobSshPresetLabel)
        self.jobSshPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobSshPresetComboBox.setObjectName(
            "jobSshPresetComboBox")
        self.formLayout3.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                   self.jobSshPresetComboBox)

        # 2 row
        self.jobPbsPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobPbsPresetLabel.setObjectName("jobPbsPresetLabel")
        self.jobPbsPresetLabel.setText(self.PBS_PRESET_LABEL)
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.jobPbsPresetLabel)
        self.jobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobPbsPresetComboBox.setObjectName(
            "jobPbsPresetComboBox")
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                   self.jobPbsPresetComboBox)

        # add button box
        self.mainVerticalLayout.addWidget(self.buttonBox)

        return dialog
