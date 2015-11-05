# -*- coding: utf-8 -*-
"""
Env dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtGui
from PyQt5 import QtWidgets

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

    def get_data(self):
        data = (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text())
        return data

    def set_data(self, data=None):
        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()


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

        # add button box
        self.mainVerticalLayout.addWidget(self.buttonBox)
