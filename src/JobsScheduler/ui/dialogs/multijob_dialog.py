# -*- coding: utf-8 -*-
"""
Multijob dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging

from PyQt5 import QtCore, QtWidgets

from ui.data.preset_data import MjPreset
from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import MultiJobNameValidator


class MultiJobDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddMultiJobDialog",
                       windowTitle="Job Scheduler - Add new MultiJob",
                       title="Add new MultiJob",
                       subtitle="Please select details to schedule set of "
                                "tasks for computation.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditMultiJobDialog",
                        windowTitle="Job Scheduler - Edit MultiJob",
                        title="Edit MultiJob",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyMultiJobDialog",
                        windowTitle="Job Scheduler - Copy MultiJob",
                        title="Copy MultiJob",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, resources=None):
        super().__init__(parent)
        # setup specific UI
        self.ui = UiMultiJobDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)
        self.set_resource_presets(resources)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super()._connect_slots()
        # specific slots
        self.ui.analysisPushButton.clicked.connect(self.handle_dir_picking)

    def valid(self):
        valid = True
        # name validator
        if not self.ui.nameLineEdit.hasAcceptableInput():
            self.ui.nameLineEdit.setStyleSheet(
                "QLineEdit { background-color: #f6989d }")  # red
            valid = False
        else:
            self.ui.nameLineEdit.setStyleSheet(
                "QLineEdit { background-color: #ffffff }")
        return valid

    def handle_dir_picking(self):
        old_dir = self.ui.analysisLineEdit.text()
        new_dir = self.ui.analysisFolderPicker \
            .getExistingDirectory(self,
                                  caption="Please select Analysis directory",
                                  directory=old_dir)
        if new_dir:
            self.ui.analysisLineEdit.setText(new_dir)

    def set_resource_presets(self, resources):
        self.ui.resourceComboBox.clear()
        if resources:
            # sort dict by list, not sure how it works
            for key in resources:
                self.ui.resourceComboBox.addItem(resources[key].name, key)

    def get_data(self):
        key = self.ui.idLineEdit.text()
        preset = MjPreset(self.ui.nameLineEdit.text())
        preset.analysis = self.ui.analysisLineEdit.text()
        preset.resource_preset = self.ui.resourceComboBox.itemData(
                    self.ui.resourceComboBox.currentIndex())
        preset.log_level = self.ui.logLevelComboBox.currentData()
        preset.number_of_processes = self.ui.numberOfProcessesSpinBox.value()
        return {
            "key": key,
            "preset": preset
        }

    def set_data(self, data=None):
        # reset validation colors
        self.ui.nameLineEdit.setStyleSheet(
                "QLineEdit { background-color: #ffffff }")
        if data:
            key = data["key"]
            preset = data["preset"]
            self.ui.idLineEdit.setText(key)
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.analysisLineEdit.setText(preset.analysis)
            self.ui.resourceComboBox.setCurrentIndex(
                self.ui.resourceComboBox.findData(preset.resource_preset))
            self.ui.logLevelComboBox.setCurrentIndex(
                self.ui.logLevelComboBox.findData(preset.log_level))
            self.ui.numberOfProcessesSpinBox.setValue(
                preset.number_of_processes)
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.analysisLineEdit.clear()
            self.ui.descriptionTextEdit.clear()
            self.ui.resourceComboBox.setCurrentIndex(0)
            self.ui.logLevelComboBox.setCurrentIndex(3)
            self.ui.numberOfProcessesSpinBox.setValue(
                self.ui.numberOfProcessesSpinBox.minimum())


class UiMultiJobDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(500, 440)

        # validators
        self.nameValidator = MultiJobNameValidator(
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
        self.nameLineEdit.setPlaceholderText("Only alphanumeric characters "
                                             "and - or _")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.nameLineEdit.setValidator(self.nameValidator)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # 2 row
        self.analysisLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.analysisLabel.setObjectName("analysisLabel")
        self.analysisLabel.setText("Analysis:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.analysisLabel)
        self.rowSplit = QtWidgets.QHBoxLayout()
        self.rowSplit.setObjectName("rowSplit")
        self.analysisLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.analysisLineEdit.setPlaceholderText("Select Analysis folder "
                                                 "path")
        self.analysisLineEdit.setObjectName("analysisLineEdit")
        self.analysisLineEdit.setProperty("clearButtonEnabled", True)
        self.rowSplit.addWidget(self.analysisLineEdit)
        self.analysisPushButton = QtWidgets.QPushButton(
            self.mainVerticalLayoutWidget)
        self.analysisPushButton.setObjectName("analysisPushButton")
        self.analysisPushButton.setText("&Browse")
        self.rowSplit.addWidget(self.analysisPushButton)
        self.analysisFolderPicker = QtWidgets.QFileDialog(
            self.mainVerticalLayoutWidget)
        self.analysisPushButton.setObjectName("analysisFolderPicker")
        self.analysisFolderPicker.setFileMode(QtWidgets.QFileDialog.Directory)
        self.analysisFolderPicker.setOption(QtWidgets.QFileDialog.ShowDirsOnly)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole,
                                  self.rowSplit)

        # 3 row
        self.descriptionLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabel.setText("Description:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.descriptionLabel)
        self.descriptionTextEdit = QtWidgets.QTextEdit(
            self.mainVerticalLayoutWidget)
        self.descriptionTextEdit.setObjectName("textEdit")
        self.descriptionTextEdit.setProperty("placeholderText",
                                             "Read only description text "
                                             "from analysis folder")
        self.descriptionTextEdit.setReadOnly(True)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.descriptionTextEdit)

        # 4 row
        self.resourceLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.resourceLabel.setObjectName("resourceLabel")
        self.resourceLabel.setText("Resource:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.resourceLabel)
        self.resourceComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.resourceComboBox.setObjectName("resourceComboBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.resourceComboBox)

        # 5 row
        self.logLevelLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.logLevelLabel.setObjectName("logLevelLabel")
        self.logLevelLabel.setText("Log Level:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.logLevelLabel)
        self.logLevelComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.logLevelComboBox.setObjectName("logLevelComboBox")
        self.logLevelComboBox.addItem(logging.getLevelName(logging.NOTSET),
                                      logging.NOTSET)
        self.logLevelComboBox.addItem(logging.getLevelName(logging.DEBUG),
                                      logging.DEBUG)
        self.logLevelComboBox.addItem(logging.getLevelName(logging.INFO),
                                      logging.INFO)
        self.logLevelComboBox.addItem(logging.getLevelName(logging.WARNING),
                                      logging.WARNING)
        self.logLevelComboBox.addItem(logging.getLevelName(logging.ERROR),
                                      logging.ERROR)
        self.logLevelComboBox.addItem(logging.getLevelName(logging.CRITICAL),
                                      logging.CRITICAL)
        self.logLevelComboBox.setCurrentIndex(3)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.logLevelComboBox)

        # 6 row
        self.numberOfProcessesLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.numberOfProcessesLabel.setObjectName("numberOfProcessesLabel")
        self.numberOfProcessesLabel.setText("Number of Processes:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.numberOfProcessesLabel)
        self.numberOfProcessesSpinBox = QtWidgets.QSpinBox(
            self.mainVerticalLayoutWidget)
        self.numberOfProcessesSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt
            .AlignVCenter)
        self.numberOfProcessesSpinBox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.numberOfProcessesSpinBox.setMinimum(1)
        self.numberOfProcessesSpinBox.setObjectName("spinBox")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.numberOfProcessesSpinBox)

        return dialog
