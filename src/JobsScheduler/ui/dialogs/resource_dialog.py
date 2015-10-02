# -*- coding: utf-8 -*-
"""
Resource dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets

from ui.dialogs.dialogs import UiFormDialog, AFormDialog


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

    def get_data(self):
        return (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text(),
                "description",
                self.ui.multiJobExecutionTypeComboBox.itemData(
                    self.ui.multiJobExecutionTypeComboBox.currentIndex()),
                self.ui.multiJobSshPresetComboBox.itemData(
                    self.ui.multiJobSshPresetComboBox.currentIndex()),
                self.ui.multiJobRemoteExecutionTypeComboBox.itemData(
                    self.ui.multiJobRemoteExecutionTypeComboBox
                        .currentIndex()),
                self.ui.multiJobPbsPresetComboBox.itemData(
                    self.ui.multiJobPbsPresetComboBox.currentIndex()),
                self.ui.jobExecutionTypeComboBox.itemData(
                    self.ui.jobExecutionTypeComboBox.currentIndex()),
                self.ui.jobSshPresetComboBox.itemData(
                    self.ui.jobSshPresetComboBox.currentIndex()),
                self.ui.jobRemoteExecutionTypeComboBox.itemData(
                    self.ui.jobRemoteExecutionTypeComboBox
                        .currentIndex()),
                self.ui.jobPbsPresetComboBox.itemData(
                    self.ui.jobPbsPresetComboBox.currentIndex()))

    def set_data(self, data=None):
        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.multiJobExecutionTypeComboBox.setCurrentIndex(
                self.ui.multiJobExecutionTypeComboBox.findData(data[3]))
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(
                self.ui.multiJobSshPresetComboBox.findData(data[4]))
            self.ui.multiJobRemoteExecutionTypeComboBox.setCurrentIndex(
                self.ui.multiJobRemoteExecutionTypeComboBox.findData(data[5]))
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(
                self.ui.multiJobPbsPresetComboBox.findData(data[6]))

            self.ui.jobExecutionTypeComboBox.setCurrentIndex(
                self.ui.jobExecutionTypeComboBox.findData(data[7]))
            self.ui.jobSshPresetComboBox.setCurrentIndex(
                self.ui.jobSshPresetComboBox.findData(data[8]))
            self.ui.jobRemoteExecutionTypeComboBox.setCurrentIndex(
                self.ui.jobRemoteExecutionTypeComboBox.findData(data[9]))
            self.ui.jobPbsPresetComboBox.setCurrentIndex(
                self.ui.jobPbsPresetComboBox.findData(data[10]))
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


class UiResourceDialog(UiFormDialog):
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
        self.multiJobExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobExecutionTypeLabel.setObjectName(
            "multiJobExecutionTypeLabel")
        self.multiJobExecutionTypeLabel.setText("MultiJob Execution Type:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobExecutionTypeLabel)
        self.multiJobExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobExecutionTypeComboBox.setObjectName(
            "multiJobExecutionTypeComboBox")
        self.multiJobExecutionTypeComboBox.addItem("LOCAL", "LOCAL")
        self.multiJobExecutionTypeComboBox.addItem("REMOTE", "REMOTE")
        self.multiJobExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.multiJobExecutionTypeComboBox)
        
        # 3 row
        self.multiJobSshPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobSshPresetLabel.setObjectName("multiJobSshPresetLabel")
        self.multiJobSshPresetLabel.setText("MultiJob SSH Preset:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobSshPresetLabel)
        self.multiJobSshPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobSshPresetComboBox.setObjectName(
            "multiJobSshPresetComboBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.multiJobSshPresetComboBox)
        
        # 4 row
        self.multiJobRemoteExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobRemoteExecutionTypeLabel.setObjectName(
            "multiJobRemoteExecutionTypeLabel")
        self.multiJobRemoteExecutionTypeLabel.setText("MultiJob Execution "
                                                      "Type:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobRemoteExecutionTypeLabel)
        self.multiJobRemoteExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobRemoteExecutionTypeComboBox.setObjectName(
            "multiJobRemoteExecutionTypeComboBox")
        self.multiJobRemoteExecutionTypeComboBox.addItem("LOCAL", "LOCAL")
        self.multiJobRemoteExecutionTypeComboBox.addItem("PBS", "PBS")
        self.multiJobRemoteExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.multiJobRemoteExecutionTypeComboBox)
        
        # 5 row
        self.multiJobPbsPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetLabel.setObjectName("multiJobPbsPresetLabel")
        self.multiJobPbsPresetLabel.setText("MultiJob PBS Preset:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobPbsPresetLabel)
        self.multiJobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetComboBox.setObjectName(
            "multiJobPbsPresetComboBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.multiJobPbsPresetComboBox)

        # 6 row
        self.jobExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobExecutionTypeLabel.setObjectName(
            "jobExecutionTypeLabel")
        self.jobExecutionTypeLabel.setText("Job Execution Type:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.jobExecutionTypeLabel)
        self.jobExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobExecutionTypeComboBox.setObjectName(
            "jobExecutionTypeComboBox")
        self.jobExecutionTypeComboBox.addItem("LOCAL", "LOCAL")
        self.jobExecutionTypeComboBox.addItem("REMOTE", "REMOTE")
        self.jobExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.jobExecutionTypeComboBox)

        # 7 row
        self.jobSshPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobSshPresetLabel.setObjectName("jobSshPresetLabel")
        self.jobSshPresetLabel.setText("Job SSH Preset:")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.jobSshPresetLabel)
        self.jobSshPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobSshPresetComboBox.setObjectName(
            "jobSshPresetComboBox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.jobSshPresetComboBox)

        # 8 row
        self.jobRemoteExecutionTypeLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobRemoteExecutionTypeLabel.setObjectName(
            "jobRemoteExecutionTypeLabel")
        self.jobRemoteExecutionTypeLabel.setText("Job Execution "
                                                 "Type:")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole,
                                  self.jobRemoteExecutionTypeLabel)
        self.jobRemoteExecutionTypeComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobRemoteExecutionTypeComboBox.setObjectName(
            "jobRemoteExecutionTypeComboBox")
        self.jobRemoteExecutionTypeComboBox.addItem("LOCAL", "LOCAL")
        self.jobRemoteExecutionTypeComboBox.addItem("PBS", "PBS")
        self.jobRemoteExecutionTypeComboBox.setCurrentIndex(0)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole,
                                  self.jobRemoteExecutionTypeComboBox)

        # 9 row
        self.jobPbsPresetLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.jobPbsPresetLabel.setObjectName("jobPbsPresetLabel")
        self.jobPbsPresetLabel.setText("Job PBS Preset:")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole,
                                  self.jobPbsPresetLabel)
        self.jobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.jobPbsPresetComboBox.setObjectName(
            "jobPbsPresetComboBox")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole,
                                  self.jobPbsPresetComboBox)
