# -*- coding: utf-8 -*-
"""
Add new MultiJob dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets
from dialogs.dialogs import UiFormDialog


class AddMultiJobDialog(QtWidgets.QDialog):
    """
    Dialog executive code with bindings and other functionality.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiAddMultiJobDialog()
        self.ui.setup_ui(self)
        self.__connect_slots__()
        self.show()

    def __connect_slots__(self):
        # QtCore.QMetaObject.connectSlotsByName(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)


class UiAddMultiJobDialog(UiFormDialog):
    """
    Dialog UI or UI extensions of basic dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.setObjectName("AddMultiJobDialog")
        dialog.setWindowTitle("Add new MultiJob")
        dialog.resize(500, 440)

        # title label
        self.titleLabel.setText("Add new MultiJob")

        # subtitle label
        self.subtitleLabel.setText("Please select details to schedule set of "
                                   "tasks for computation.")
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

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.analysisLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.analysisLineEdit.setPlaceholderText("Select Analysis folder "
                                                 "path")
        self.analysisLineEdit.setObjectName("analysisLineEdit")
        self.analysisLineEdit.setProperty("clearButtonEnabled", True)
        self.horizontalLayout_3.addWidget(self.analysisLineEdit)
        self.toolButton = QtWidgets.QToolButton(self.mainVerticalLayoutWidget)
        self.toolButton.setObjectName("toolButton")
        self.toolButton.setText("...")
        self.horizontalLayout_3.addWidget(self.toolButton)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole,
                                  self.horizontalLayout_3)

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
