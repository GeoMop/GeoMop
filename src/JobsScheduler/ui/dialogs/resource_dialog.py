# -*- coding: utf-8 -*-
"""
Resource dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtGui, QtWidgets

from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import PresetNameValidator, ValidationColorizer


class ResourceDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddResourcehDialog",
                       windowTitle="Job Scheduler - Add new Resource Preset",
                       title="Add new Resource Preset",
                       subtitle="Please select details for new Resource "
                                "preset.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditResourceDialog",
                        windowTitle="Job Scheduler - Edit Resource Preset",
                        title="Edit Resource Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyResourceDialog",
                        windowTitle="Job Scheduler - Copy Resource Preset",
                        title="Copy Resource Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, purpose=PURPOSE_ADD, data=None):
        super(ResourceDialog, self).__init__(parent)
        # setup specific UI
        self.ui = UiResourceDialog()
        self.ui.setup_ui(self)

        # set purpose
        self.set_purpose(purpose, data)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super(ResourceDialog, self)._connect_slots()
        # specific slots
        self.ui.multiJobExecutionTypeComboBox.currentIndexChanged.connect(
            self._handle_mj_exec_change)
        self.ui.multiJobRemoteExecutionTypeComboBox.currentIndexChanged \
            .connect(self._handle_mj_delegator_exec_change)
        self.ui.jobExecutionTypeComboBox.currentIndexChanged.connect(
            self._handle_j_exec_change)
        self.ui.jobRemoteExecutionTypeComboBox.currentIndexChanged \
            .connect(self._handle_j_remote_exec_change)

    def valid(self):
        valid = True
        if not ValidationColorizer.colorize_by_validator(
                self.ui.nameLineEdit):
            valid = False
        return valid

    def _handle_mj_exec_change(self, index):
        if index == self.ui.multiJobExecutionTypeComboBox.findText(
                self.ui.EXEC_LABEL):
            self.ui.jobExecutionTypeComboBox.clear()
            self.ui.jobExecutionTypeComboBox.addItems([self.ui.EXEC_LABEL,
                                                       self.ui.REMOTE_LABEL])
            self.ui.multiJobSshPresetComboBox.setDisabled(True)
            self.ui.multiJobRemoteExecutionTypeComboBox.setDisabled(True)
            self.ui.multiJobPbsPresetComboBox.setDisabled(True)
        else:
            self.ui.multiJobSshPresetComboBox.setDisabled(False)
            self.ui.multiJobRemoteExecutionTypeComboBox.setDisabled(False)
            self._handle_mj_delegator_exec_change(
                self.ui.multiJobRemoteExecutionTypeComboBox.currentIndex())

    def _handle_mj_delegator_exec_change(self, index):
        if index == self.ui.multiJobRemoteExecutionTypeComboBox.findText(
                self.ui.EXEC_LABEL):
            self.ui.multiJobPbsPresetComboBox.setDisabled(True)
            self.ui.jobExecutionTypeComboBox.clear()
            self.ui.jobExecutionTypeComboBox.addItems([
                self.ui.REMOTE_LABEL, self.ui.PBS_LABEL])
        else:
            self.ui.multiJobPbsPresetComboBox.setDisabled(False)
            self.ui.jobExecutionTypeComboBox.clear()
            self.ui.jobExecutionTypeComboBox.addItems([
                self.ui.REMOTE_LABEL, self.ui.PBS_LABEL])

    def _handle_j_exec_change(self, index):
        if index == self.ui.jobExecutionTypeComboBox.findText(
                self.ui.EXEC_LABEL):
            self.ui.jobSshPresetComboBox.setDisabled(True)
            self.ui.jobRemoteExecutionTypeComboBox.setDisabled(True)
            self.ui.jobPbsPresetComboBox.setDisabled(True)
        elif index == self.ui.jobExecutionTypeComboBox.findText(
                self.ui.PBS_LABEL):
            self.ui.jobSshPresetComboBox.setDisabled(True)
            self.ui.jobRemoteExecutionTypeComboBox.setDisabled(True)
            self.ui.jobPbsPresetComboBox.setDisabled(False)
        else:
            self.ui.jobSshPresetComboBox.setDisabled(False)
            self.ui.jobRemoteExecutionTypeComboBox.setDisabled(False)
            if self.ui.multiJobRemoteExecutionTypeComboBox.currentIndex() == \
                    self.ui.multiJobRemoteExecutionTypeComboBox.findText(
                        self.ui.PBS_LABEL):
                self.ui.jobRemoteExecutionTypeComboBox.clear()
                self.ui.jobRemoteExecutionTypeComboBox.addItems([
                    self.ui.PBS_LABEL])
            else:
                self.ui.jobRemoteExecutionTypeComboBox.clear()
                self.ui.jobRemoteExecutionTypeComboBox.addItems([
                    self.ui.PBS_LABEL, self.ui.EXEC_LABEL])
            self._handle_j_remote_exec_change(
                self.ui.jobRemoteExecutionTypeComboBox.currentIndex())

    def _handle_j_remote_exec_change(self, index):
        if index > 0 and index == \
                self.ui.jobRemoteExecutionTypeComboBox.findText(
                self.ui.EXEC_LABEL):
            self.ui.jobPbsPresetComboBox.setDisabled(True)
        else:
            self.ui.jobPbsPresetComboBox.setDisabled(False)

    def set_pbs_presets(self, pbs):
        self.ui.multiJobPbsPresetComboBox.clear()
        self.ui.jobPbsPresetComboBox.clear()
        if pbs:
            # sort dict by list, not sure how it works
            for idx in sorted(pbs, key=pbs.get, reverse=False):
                self.ui.multiJobPbsPresetComboBox.addItem(pbs[idx][0], idx)
                self.ui.jobPbsPresetComboBox.addItem(pbs[idx][0], idx)

    def set_ssh_presets(self, ssh):
        self.ui.multiJobSshPresetComboBox.clear()
        self.ui.jobSshPresetComboBox.clear()
        if ssh:
            # sort dict by list, not sure how it works
            for idx in sorted(ssh, key=ssh.get, reverse=False):
                self.ui.multiJobSshPresetComboBox.addItem(ssh[idx][0], idx)
                self.ui.jobSshPresetComboBox.addItem(ssh[idx][0], idx)

    def set_env_presets(self, env):
        self.ui.mjEnvPresetComboBox.clear()
        self.ui.jobEnvPresetComboBox.clear()
        if env:
            # sort dict by list, not sure how it works
            for idx in sorted(env, key=env.get, reverse=False):
                self.ui.mjEnvPresetComboBox.addItem(env[idx][0], idx)
                self.ui.jobEnvPresetComboBox.addItem(env[idx][0], idx)

    def get_data(self):
        return (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text(),
                "description",
                self.ui.multiJobExecutionTypeComboBox.itemText(
                    self.ui.multiJobExecutionTypeComboBox.currentIndex()) if
                self.ui.multiJobExecutionTypeComboBox.isEnabled() else None,
                self.ui.multiJobSshPresetComboBox.itemData(
                    self.ui.multiJobSshPresetComboBox.currentIndex()) if
                self.ui.multiJobSshPresetComboBox.isEnabled() else None,
                self.ui.multiJobRemoteExecutionTypeComboBox.itemText(
                    self.ui.multiJobRemoteExecutionTypeComboBox
                        .currentIndex()) if
                self.ui.multiJobRemoteExecutionTypeComboBox.isEnabled() else
                None,
                self.ui.multiJobPbsPresetComboBox.itemData(
                    self.ui.multiJobPbsPresetComboBox.currentIndex()) if
                self.ui.multiJobPbsPresetComboBox.isEnabled() else None,
                self.ui.jobExecutionTypeComboBox.itemText(
                    self.ui.jobExecutionTypeComboBox.currentIndex()),
                self.ui.jobSshPresetComboBox.itemData(
                    self.ui.jobSshPresetComboBox.currentIndex()) if
                self.ui.jobSshPresetComboBox.isEnabled() else None,
                self.ui.jobRemoteExecutionTypeComboBox.itemText(
                    self.ui.jobRemoteExecutionTypeComboBox
                        .currentIndex()) if
                self.ui.jobRemoteExecutionTypeComboBox.isEnabled() else None,
                self.ui.jobPbsPresetComboBox.itemData(
                    self.ui.jobPbsPresetComboBox.currentIndex()) if
                self.ui.jobPbsPresetComboBox.isEnabled() else None,
                self.ui.mjEnvPresetComboBox.itemData(
                    self.ui.mjEnvPresetComboBox.currentIndex()),
                self.ui.jobEnvPresetComboBox.itemData(
                    self.ui.jobEnvPresetComboBox.currentIndex()))

    def set_data(self, data=None):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)

        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.multiJobExecutionTypeComboBox.setCurrentIndex(
                self.ui.multiJobExecutionTypeComboBox.findText(data[3]))
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(
                self.ui.multiJobSshPresetComboBox.findData(data[4]))
            self.ui.multiJobRemoteExecutionTypeComboBox.setCurrentIndex(
                self.ui.multiJobRemoteExecutionTypeComboBox.findText(data[5]))
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(
                self.ui.multiJobPbsPresetComboBox.findData(data[6]))

            self.ui.jobExecutionTypeComboBox.setCurrentIndex(
                self.ui.jobExecutionTypeComboBox.findText(data[7]))
            self.ui.jobSshPresetComboBox.setCurrentIndex(
                self.ui.jobSshPresetComboBox.findData(data[8]))
            self.ui.jobRemoteExecutionTypeComboBox.setCurrentIndex(
                self.ui.jobRemoteExecutionTypeComboBox.findText(data[9]))
            self.ui.jobPbsPresetComboBox.setCurrentIndex(
                self.ui.jobPbsPresetComboBox.findData(data[10]))

            self.ui.mjEnvPresetComboBox.setCurrentIndex(
                self.ui.mjEnvPresetComboBox.findData(data[11]))
            self.ui.jobEnvPresetComboBox.setCurrentIndex(
                self.ui.jobEnvPresetComboBox.findData(data[12]))

        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.multiJobExecutionTypeComboBox.setCurrentIndex(-1)
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(-1)
            self.ui.multiJobRemoteExecutionTypeComboBox.setCurrentIndex(-1)
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(-1)

            self.ui.jobExecutionTypeComboBox.setCurrentIndex(-1)
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(-1)
            self.ui.jobRemoteExecutionTypeComboBox.setCurrentIndex(-1)
            self.ui.jobPbsPresetComboBox.setCurrentIndex(-1)

            self.ui.mjEnvPresetComboBox.setCurrentIndex(-1)
            self.ui.jobEnvPresetComboBox.setCurrentIndex(-1)


class UiResourceDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """
    EXECUTE_USING_LABEL = "Execute using:"
    EXECUTION_TYPE_LABEL = "Execution type:"
    SSH_PRESET_LABEL = "SSH preset:"
    PBS_PRESET_LABEL = "PBS preset:"
    MJ_ENV_LABEL = "MultiJob environment:"
    JOB_ENV_LABEL = "Job environment:"

    EXEC_LABEL = "EXEC"
    DELEGATOR_LABEL = "DELEGATOR"
    REMOTE_LABEL = "REMOTE"
    PBS_LABEL = "PBS"

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        # validators
        self.nameValidator = PresetNameValidator(
            self.mainVerticalLayoutWidget)

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
        self.multiJobExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobExecutionTypeLabel.setObjectName(
            "multiJobExecutionTypeLabel")
        self.multiJobExecutionTypeLabel.setText(self.EXECUTE_USING_LABEL)
        self.formLayout2.setWidget(0, QtWidgets.QFormLayout.LabelRole,
                                   self.multiJobExecutionTypeLabel)
        self.multiJobExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobExecutionTypeComboBox.setObjectName(
            "multiJobExecutionTypeComboBox")
        self.multiJobExecutionTypeComboBox.addItems([self.EXEC_LABEL,
                                                     self.DELEGATOR_LABEL])
        self.multiJobExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout2.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                   self.multiJobExecutionTypeComboBox)

        # 2 row
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

        # 3 row
        self.multiJobRemoteExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobRemoteExecutionTypeLabel.setObjectName(
            "multiJobRemoteExecutionTypeLabel")
        self.multiJobRemoteExecutionTypeLabel.setText(
            self.EXECUTION_TYPE_LABEL)
        self.formLayout2.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.multiJobRemoteExecutionTypeLabel)
        self.multiJobRemoteExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobRemoteExecutionTypeComboBox.setObjectName(
            "multiJobRemoteExecutionTypeComboBox")
        self.multiJobRemoteExecutionTypeComboBox.addItems([self.EXEC_LABEL,
                                                           self.PBS_LABEL])
        self.multiJobRemoteExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout2.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                   self.multiJobRemoteExecutionTypeComboBox)

        # 4 row
        self.multiJobPbsPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetLabel.setObjectName("multiJobPbsPresetLabel")
        self.multiJobPbsPresetLabel.setText(self.PBS_PRESET_LABEL)
        self.formLayout2.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                   self.multiJobPbsPresetLabel)
        self.multiJobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetComboBox.setObjectName(
            "multiJobPbsPresetComboBox")
        self.formLayout2.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                   self.multiJobPbsPresetComboBox)

        # 5 row
        self.mjEnvPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.mjEnvPresetLabel.setObjectName("mjEnvPresetLabel")
        self.mjEnvPresetLabel.setText(self.MJ_ENV_LABEL)
        self.formLayout2.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                   self.mjEnvPresetLabel)
        self.mjEnvPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.mjEnvPresetComboBox.setObjectName(
            "mjEnvPresetComboBox")
        self.formLayout2.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                   self.mjEnvPresetComboBox)

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
        self.jobExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobExecutionTypeLabel.setObjectName(
            "jobExecutionTypeLabel")
        self.jobExecutionTypeLabel.setText(self.EXECUTE_USING_LABEL)
        self.formLayout3.setWidget(0, QtWidgets.QFormLayout.LabelRole,
                                   self.jobExecutionTypeLabel)
        self.jobExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobExecutionTypeComboBox.setObjectName(
            "jobExecutionTypeComboBox")
        self.jobExecutionTypeComboBox.addItems([self.EXEC_LABEL,
                                                self.REMOTE_LABEL,
                                                self.PBS_LABEL])
        self.jobExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout3.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                   self.jobExecutionTypeComboBox)

        # 2 row
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

        # 3 row
        self.jobRemoteExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobRemoteExecutionTypeLabel.setObjectName(
            "jobRemoteExecutionTypeLabel")
        self.jobRemoteExecutionTypeLabel.setText(self.EXECUTION_TYPE_LABEL)
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.jobRemoteExecutionTypeLabel)
        self.jobRemoteExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobRemoteExecutionTypeComboBox.setObjectName(
            "jobRemoteExecutionTypeComboBox")
        self.jobRemoteExecutionTypeComboBox.addItems([self.EXEC_LABEL,
                                                      self.PBS_LABEL])
        self.jobRemoteExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                   self.jobRemoteExecutionTypeComboBox)

        # 4 row
        self.jobPbsPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobPbsPresetLabel.setObjectName("jobPbsPresetLabel")
        self.jobPbsPresetLabel.setText(self.PBS_PRESET_LABEL)
        self.formLayout3.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                   self.jobPbsPresetLabel)
        self.jobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobPbsPresetComboBox.setObjectName(
            "jobPbsPresetComboBox")
        self.formLayout3.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                   self.jobPbsPresetComboBox)

        # 5 row
        self.jobEnvPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobEnvPresetLabel.setObjectName("jobEnvPresetLabel")
        self.jobEnvPresetLabel.setText(self.JOB_ENV_LABEL)
        self.formLayout3.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                   self.jobEnvPresetLabel)
        self.jobEnvPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobEnvPresetComboBox.setObjectName(
            "jobEnvPresetComboBox")
        self.formLayout3.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                   self.jobEnvPresetComboBox)

        # add button box
        self.mainVerticalLayout.addWidget(self.buttonBox)
