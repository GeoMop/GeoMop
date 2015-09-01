# -*- coding: utf-8 -*-
"""
MultiJob dialogs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets

from ui.dialogs.dialogs import UiFormDialog


class MultiJobDialog(QtWidgets.QDialog):
    """
    Dialog executive code with bindings and other functionality.
    """
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

    def __init__(self, parent=None, purpose=PURPOSE_ADD):
        super(MultiJobDialog, self).__init__(parent)
        self.ui = UiMultiJobDialog()
        self.ui.setup_ui(self)

        self._purpose_ = None
        self.set_purpose(purpose)

        self._connect_slots_()
        self.show()

    def set_purpose(self, purpose):
        self._purpose_ = purpose
        self.setObjectName(purpose["objectName"])
        self.setWindowTitle(purpose["windowTitle"])

        # title label
        self.ui.titleLabel.setText(purpose["title"])

        # subtitle label
        self.ui.subtitleLabel.setText(purpose["subtitle"])

    def get_data(self):
        pass

    def set_data(self, data):
        pass

    def _connect_slots_(self):
        # QtCore.QMetaObject.connectSlotsByName(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)


class UiMultiJobDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(500, 440)

        # form layout
        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setPlaceholderText("Only alphanumeric characters "
                                             "and - or _")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # 2 row
        self.analysisLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.analysisLabel.setObjectName("analysisLabel")
        self.analysisLabel.setText("Analysis:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
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
        self.toolButton = QtWidgets.QToolButton(self.mainVerticalLayoutWidget)
        self.toolButton.setObjectName("toolButton")
        self.toolButton.setText("...")
        self.rowSplit.addWidget(self.toolButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole,
                                  self.rowSplit)

        # 3 row
        self.descriptionLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.descriptionLabel.setText("Description:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.descriptionLabel)
        self.textEdit = QtWidgets.QTextEdit(self.mainVerticalLayoutWidget)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setProperty("placeholderText", "Read only description "
                                                     "text from analysis "
                                                     "folder")
        self.textEdit.setReadOnly(True)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.textEdit)

        # 4 row
        self.resourceLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.resourceLabel.setObjectName("resourceLabel")
        self.resourceLabel.setText("Resource:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.resourceLabel)
        self.resourceComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.resourceComboBox.setObjectName("resourceComboBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.resourceComboBox)

        # 5 row
        self.logLevelLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.logLevelLabel.setObjectName("logLevelLabel")
        self.logLevelLabel.setText("Log Level:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.logLevelLabel)
        self.logLevelComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.logLevelComboBox.setObjectName("logLevelComboBox")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.logLevelComboBox)

        # 6 row
        self.numberOfProcessesLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.numberOfProcessesLabel.setObjectName("numberOfProcessesLabel")
        self.numberOfProcessesLabel.setText("Number of Processes:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.numberOfProcessesLabel)
        self.spinBox = QtWidgets.QSpinBox(self.mainVerticalLayoutWidget)
        self.spinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt
            .AlignVCenter)
        self.spinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.spinBox.setMinimum(1)
        self.spinBox.setObjectName("spinBox")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.spinBox)
