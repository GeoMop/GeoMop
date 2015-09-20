# -*- coding: utf-8 -*-
"""
Multijob dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets
import logging

from ui.dialogs.dialogs import UiFormDialog, AbstractFormDialog


class MultiJobDialog(AbstractFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
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

    def __init__(self, parent=None, purpose=PURPOSE_ADD, resources=None,
                 data=None):
        super(MultiJobDialog, self).__init__(parent)
        # setup specific UI
        self.ui = UiMultiJobDialog()
        self.ui.setup_ui(self)

        # set purpose, data and resources
        self.set_purpose(purpose, data)
        self.set_resources(resources)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super(MultiJobDialog, self)._connect_slots()
        # specific slots
        self.ui.analysisPushButton.clicked.connect(self.handle_dir_picking)

    def handle_dir_picking(self):
        old_dir = self.ui.analysisLineEdit.text()
        new_dir = self.ui.analysisFolderPicker \
            .getExistingDirectory(self,
                                  caption="Please select Analysis directory",
                                  directory=old_dir)
        if new_dir:
            self.ui.analysisLineEdit.setText(new_dir)

    def set_resources(self, resources):
        self.ui.resourceComboBox.clear()
        if resources:
            # sort dict by list, not sure how it works
            for idx in sorted(resources, key=resources.get, reverse=False):
                self.ui.resourceComboBox.addItem(resources[idx][0], idx)

    def get_data(self):
        data = (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text(),
                self.ui.analysisLineEdit.text(),
                self.ui.descriptionTextEdit.toPlainText(),
                self.ui.resourceComboBox.itemData(
                    self.ui.resourceComboBox.currentIndex()),
                self.ui.logLevelComboBox.currentText(),
                self.ui.numberOfProcessesSpinBox.value())
        return data

    def set_data(self, data=None):
        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.analysisLineEdit.setText(data[2])
            self.ui.descriptionTextEdit.setText(data[3])
            self.ui.resourceComboBox.setCurrentIndex(
                self.ui.resourceComboBox.findData(data[4]))
            self.ui.logLevelComboBox.setCurrentIndex(
                self.ui.logLevelComboBox.findText(data[5]))
            self.ui.numberOfProcessesSpinBox.setValue(data[6])
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.analysisLineEdit.clear()
            self.ui.descriptionTextEdit.clear()
            self.ui.resourceComboBox.setCurrentIndex(0)
            self.ui.logLevelComboBox.setCurrentIndex(1)
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
        self.logLevelComboBox.setCurrentIndex(0)
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
