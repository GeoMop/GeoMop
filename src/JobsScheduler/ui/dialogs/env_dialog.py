# -*- coding: utf-8 -*-
"""
Env dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from ui.dialogs.dialogs import UiFormDialog, AFormDialog


class EnvDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddEnvDialog",
                       windowTitle="Job Scheduler - Add new Environment "
                                   "Preset",
                       title="Add new Environment Preset",
                       subtitle="Please select details for new Environment "
                                "preset.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditEnvDialog",
                        windowTitle="Job Scheduler - Edit Environment Preset",
                        title="Edit Environment Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyEnvDialog",
                        windowTitle="Job Scheduler - Copy Environment Preset",
                        title="Copy Environment Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, purpose=PURPOSE_ADD, data=None):
        super(EnvDialog, self).__init__(parent)
        # setup specific UI
        self.ui = UiEnvDialog()
        self.ui.setup_ui(self)

        # set purpose
        self.set_purpose(purpose, data)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super(EnvDialog, self)._connect_slots()
        # specific slots
        self.ui.sclEnableCheckBox.stateChanged.connect(
            lambda state: self.ui.sclEnableLineEdit.setDisabled(not state)
        )
        self.ui.addModuleCheckBox.stateChanged.connect(
            lambda state: self.ui.addModuleLineEdit.setDisabled(not state)
        )
        self.ui.mpiSclEnableCheckBox.stateChanged.connect(
            lambda state: self.ui.mpiSclEnableLineEdit.setDisabled(not
                                                                   state)
        )
        self.ui.mpiAddModuleCheckBox.stateChanged.connect(
            lambda state: self.ui.mpiAddModuleLineEdit.setDisabled(not state)
        )

    def get_data(self):
        data = (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text(),
                "description",
                self.ui.pythonExecLineEdit.text(),
                self.ui.sclEnableLineEdit.text()
                if self.ui.sclEnableCheckBox.isChecked() else None,
                self.ui.addModuleLineEdit.text()
                if self.ui.addModuleCheckBox.isChecked() else None,
                self.ui.mpiSclEnableLineEdit.text()
                if self.ui.mpiSclEnableCheckBox.isChecked() else None,
                self.ui.mpiAddModuleLineEdit.text()
                if self.ui.mpiAddModuleCheckBox.isChecked() else None,
                self.ui.mpiccPathLineEdit.text())
        return data

    def set_data(self, data=None):
        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.pythonExecLineEdit.setText(data[3])
            if data[4]:
                self.ui.sclEnableCheckBox.setCheckState(Qt.Checked)
                self.ui.sclEnableLineEdit.setText(data[4])
            if data[5]:
                self.ui.addModuleCheckBox.setCheckState(Qt.Checked)
                self.ui.addModuleLineEdit.setText(data[5])
            if data[6]:
                self.ui.mpiSclEnableCheckBox.setCheckState(Qt.Checked)
                self.ui.mpiSclEnableLineEdit.setText(data[6])
            if data[7]:
                self.ui.mpiAddModuleCheckBox.setCheckState(Qt.Checked)
                self.ui.mpiAddModuleLineEdit.setText(data[7])
            self.ui.mpiccPathLineEdit.setText(data[8])

        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.pythonExecLineEdit.clear()
            self.ui.sclEnableCheckBox.setCheckState(Qt.Unchecked)
            self.ui.sclEnableLineEdit.clear()
            self.ui.addModuleCheckBox.setCheckState(Qt.Unchecked)
            self.ui.addModuleLineEdit.clear()
            self.ui.mpiSclEnableCheckBox.setCheckState(Qt.Unchecked)
            self.ui.mpiSclEnableLineEdit.clear()
            self.ui.mpiAddModuleCheckBox.setCheckState(Qt.Unchecked)
            self.ui.mpiAddModuleLineEdit.clear()
            self.ui.mpiccPathLineEdit.clear()


class UiEnvDialog(UiFormDialog):
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

        # python label
        self.pythonLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.pythonLabel.setObjectName("pythonLabel")
        self.pythonLabel.setFont(labelFont)
        self.pythonLabel.setText("Python")
        self.mainVerticalLayout.addWidget(self.pythonLabel)

        # form layout2
        self.formLayout2 = QtWidgets.QFormLayout()
        self.formLayout2.setObjectName("formLayout2")
        self.formLayout2.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout2)

        # 1 row
        self.pythonExecLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.pythonExecLabel.setObjectName("pythonExecLabel")
        self.pythonExecLabel.setText("Interpreter:")
        self.formLayout2.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                   self.pythonExecLabel)
        self.pythonExecLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.pythonExecLineEdit.setObjectName("pythonExecLineEdit")
        self.pythonExecLineEdit.setPlaceholderText("for example: python3")
        self.pythonExecLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout2.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                   self.pythonExecLineEdit)

        # 2 row
        self.sclEnableLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.sclEnableLabel.setObjectName("sclEnableLabel")
        self.sclEnableLabel.setText("SCL Enable:")
        self.formLayout2.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.sclEnableLabel)
        self.sclEnableRowSplit = QtWidgets.QHBoxLayout()
        self.sclEnableRowSplit.setObjectName("sclEnableRowSplit")
        self.sclEnableLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.sclEnableLineEdit.setObjectName("sclEnableLineEdit")
        self.sclEnableLineEdit.setPlaceholderText("for example: python33")
        self.sclEnableLineEdit.setProperty("clearButtonEnabled", True)
        self.sclEnableLineEdit.setDisabled(True)
        self.sclEnableCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.sclEnableCheckBox.setObjectName("sclEnableCheckBox")
        self.sclEnableRowSplit.addWidget(self.sclEnableCheckBox)
        self.sclEnableRowSplit.addWidget(self.sclEnableLineEdit)
        self.formLayout2.setLayout(2, QtWidgets.QFormLayout.FieldRole,
                                   self.sclEnableRowSplit)

        # 3 row
        self.addModuleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.addModuleLabel.setObjectName("addModuleLabel")
        self.addModuleLabel.setText("Add module:")
        self.formLayout2.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                   self.addModuleLabel)
        self.addModuleRowSplit = QtWidgets.QHBoxLayout()
        self.addModuleRowSplit.setObjectName("addModuleRowSplit")
        self.addModuleLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.addModuleLineEdit.setObjectName("addModuleLineEdit")
        self.addModuleLineEdit.setPlaceholderText("for example: "
                                                  "python34-module-gcc")
        self.addModuleLineEdit.setProperty("clearButtonEnabled", True)
        self.addModuleLineEdit.setDisabled(True)
        self.addModuleCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.addModuleCheckBox.setObjectName("addModuleCheckBox")
        self.addModuleRowSplit.addWidget(self.addModuleCheckBox)
        self.addModuleRowSplit.addWidget(self.addModuleLineEdit)
        self.formLayout2.setLayout(3, QtWidgets.QFormLayout.FieldRole,
                                   self.addModuleRowSplit)

        # divider
        self.formDivider1 = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.formDivider1.setObjectName("formDivider")
        self.formDivider1.setFrameShape(QtWidgets.QFrame.HLine)
        self.formDivider1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.formDivider1)

        # mpi label
        self.mpiLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.mpiLabel.setObjectName("mpiLabel")
        self.mpiLabel.setFont(labelFont)
        self.mpiLabel.setText("Mpi")
        self.mainVerticalLayout.addWidget(self.mpiLabel)

        # form layout3
        self.mainVerticalLayout.removeWidget(self.buttonBox)
        self.formLayout3 = QtWidgets.QFormLayout()
        self.formLayout3.setObjectName("formLayout3")
        self.formLayout3.setContentsMargins(0, 5, 0, 5)
        self.mainVerticalLayout.addLayout(self.formLayout3)

        # 1 row
        self.mpiSclEnableLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.mpiSclEnableLabel.setObjectName("mpiSclEnableLabel")
        self.mpiSclEnableLabel.setText("SCL Enable:")
        self.formLayout3.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                   self.mpiSclEnableLabel)
        self.mpiSclEnableRowSplit = QtWidgets.QHBoxLayout()
        self.mpiSclEnableRowSplit.setObjectName("mpiSclEnableRowSplit")
        self.mpiSclEnableLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.mpiSclEnableLineEdit.setObjectName("mpiSclEnableLineEdit")
        self.mpiSclEnableLineEdit.setPlaceholderText("for example: "
                                                     "rock-openmpi")
        self.mpiSclEnableLineEdit.setProperty("clearButtonEnabled", True)
        self.mpiSclEnableLineEdit.setDisabled(True)
        self.mpiSclEnableCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.mpiSclEnableCheckBox.setObjectName("mpiSclEnableCheckBox")
        self.mpiSclEnableRowSplit.addWidget(self.mpiSclEnableCheckBox)
        self.mpiSclEnableRowSplit.addWidget(self.mpiSclEnableLineEdit)
        self.formLayout3.setLayout(1, QtWidgets.QFormLayout.FieldRole,
                                   self.mpiSclEnableRowSplit)

        # 2 row
        self.mpiAddModuleLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.mpiAddModuleLabel.setObjectName("mpiAddModuleLabel")
        self.mpiAddModuleLabel.setText("Add module:")
        self.formLayout3.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                   self.mpiAddModuleLabel)
        self.mpiAddModuleRowSplit = QtWidgets.QHBoxLayout()
        self.mpiAddModuleRowSplit.setObjectName("mpiAddModuleRowSplit")
        self.mpiAddModuleLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.mpiAddModuleLineEdit.setObjectName("mpiAddModuleLineEdit")
        self.mpiAddModuleLineEdit.setPlaceholderText("for example: "
                                                     "rock-openmpi")
        self.mpiAddModuleLineEdit.setProperty("clearButtonEnabled", True)
        self.mpiAddModuleLineEdit.setDisabled(True)
        self.mpiAddModuleCheckBox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.mpiAddModuleCheckBox.setObjectName("mpiAddModuleCheckBox")
        self.mpiAddModuleRowSplit.addWidget(self.mpiAddModuleCheckBox)
        self.mpiAddModuleRowSplit.addWidget(self.mpiAddModuleLineEdit)
        self.formLayout3.setLayout(2, QtWidgets.QFormLayout.FieldRole,
                                   self.mpiAddModuleRowSplit)

        # 3 row
        self.mpiccPathLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.mpiccPathLabel.setObjectName("mpiccPathLabel")
        self.mpiccPathLabel.setText("Mpicc path:")
        self.formLayout3.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                   self.mpiccPathLabel)
        self.mpiccPathLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.mpiccPathLineEdit.setObjectName("mpiccPathLineEdit")
        self.mpiccPathLineEdit.setPlaceholderText("alternative path to mpicc")
        self.mpiccPathLineEdit.setProperty("clearButtonEnabled", True)
        self.formLayout3.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                   self.mpiccPathLineEdit)
        
        # add button box
        self.mainVerticalLayout.addWidget(self.buttonBox)
