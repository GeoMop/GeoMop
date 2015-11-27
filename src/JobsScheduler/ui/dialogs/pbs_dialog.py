# -*- coding: utf-8 -*-
"""
Pbs dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets

from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import PresetNameValidator, WalltimeValidator, \
    MemoryValidator, ScratchValidator, ValidationColorizer


class PbsDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # Purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddPbsDialog",
                       windowTitle="Job Scheduler - Add new PBS Preset",
                       title="Add new PBS Preset",
                       subtitle="Please select details for new PBS preset.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditPbsDialog",
                        windowTitle="Job Scheduler - Edit PBS Preset",
                        title="Edit PBS Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyPbsDialog",
                        windowTitle="Job Scheduler - Copy PBS Preset",
                        title="Copy PBS Preset",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, purpose=PURPOSE_ADD, data=None):
        super(PbsDialog, self).__init__(parent)
        # setup specific UI
        self.ui = UiPbsDialog()
        self.ui.setup_ui(self)

        # set purpose
        self.set_purpose(purpose, data)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super(PbsDialog, self)._connect_slots()
        # specific slots

    def valid(self):
        valid = True
        if not ValidationColorizer.colorize_by_validator(
                self.ui.nameLineEdit):
            valid = False
        if not ValidationColorizer.colorize_by_validator(
                self.ui.walltimeLineEdit):
            valid = False
        if not ValidationColorizer.colorize_by_validator(
                self.ui.memoryLineEdit):
            valid = False
        if not ValidationColorizer.colorize_by_validator(
                self.ui.scratchLineEdit):
            valid = False
        return valid

    def get_data(self):
        data = (self.ui.idLineEdit.text(),
                self.ui.nameLineEdit.text(),
                (self.ui.walltimeLineEdit.text() + ", " +  # description
                 str(self.ui.nodesSpinBox.value()) + ", " +
                 str(self.ui.ppnSpinBox.value()) + ", " +
                 self.ui.memoryLineEdit.text() + ", " +
                 self.ui.scratchLineEdit.text()),
                self.ui.walltimeLineEdit.text(),
                self.ui.nodesSpinBox.value(),
                self.ui.ppnSpinBox.value(),
                self.ui.memoryLineEdit.text(),
                self.ui.scratchLineEdit.text())
        return data

    def set_data(self, data=None):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)
        ValidationColorizer.colorize_white(self.ui.walltimeLineEdit)
        ValidationColorizer.colorize_white(self.ui.memoryLineEdit)
        ValidationColorizer.colorize_white(self.ui.scratchLineEdit)

        if data:
            self.ui.idLineEdit.setText(data[0])
            self.ui.nameLineEdit.setText(data[1])
            self.ui.walltimeLineEdit.setText(data[3])
            self.ui.nodesSpinBox.setValue(data[4])
            self.ui.ppnSpinBox.setValue(data[5])
            self.ui.memoryLineEdit.setText(data[6])
            self.ui.scratchLineEdit.setText(data[7])
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.walltimeLineEdit.clear()
            self.ui.nodesSpinBox.setValue(self.ui.nodesSpinBox.minimum())
            self.ui.ppnSpinBox.setValue(self.ui.ppnSpinBox.minimum())
            self.ui.memoryLineEdit.clear()
            self.ui.scratchLineEdit.clear()


class UiPbsDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        # validators
        self.nameValidator = PresetNameValidator(
            self.mainVerticalLayoutWidget)
        self.walltimeValidator = WalltimeValidator(
            self.mainVerticalLayoutWidget)
        self.memoryValidator = MemoryValidator(
            self.mainVerticalLayoutWidget)
        self.scratchValidator = ScratchValidator(
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

        # 2 row
        self.walltimeLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.walltimeLabel.setObjectName("walltimeLabel")
        self.walltimeLabel.setText("Walltime:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.walltimeLabel)
        self.walltimeLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.walltimeLineEdit.setObjectName("walltimeLineEdit")
        self.walltimeLineEdit.setPlaceholderText("1d4h or 20h")
        self.walltimeLineEdit.setProperty("clearButtonEnabled", True)
        self.walltimeLineEdit.setValidator(self.walltimeValidator)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.walltimeLineEdit)

        # 3 row
        self.nodesLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nodesLabel.setObjectName("nodesLabel")
        self.nodesLabel.setText("Specify number of nodes:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.nodesLabel)
        self.nodesSpinBox = QtWidgets.QSpinBox(
            self.mainVerticalLayoutWidget)
        self.nodesSpinBox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.nodesSpinBox.setMinimum(1)
        self.nodesSpinBox.setMaximum(1000)
        self.nodesSpinBox.setObjectName("nodesSpinBox")
        self.nodesSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt
            .AlignVCenter)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.nodesSpinBox)

        # 4 row
        self.ppnLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.ppnLabel.setObjectName("ppnLabel")
        self.ppnLabel.setText("Processors per Node:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.ppnLabel)
        self.ppnSpinBox = QtWidgets.QSpinBox(
            self.mainVerticalLayoutWidget)
        self.ppnSpinBox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.ppnSpinBox.setMinimum(1)
        self.ppnSpinBox.setMaximum(100)
        self.ppnSpinBox.setObjectName("nodesSpinBox")
        self.ppnSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt
            .AlignVCenter)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.ppnSpinBox)

        # 5 row
        self.memoryLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.memoryLabel.setObjectName("walltimeLabel")
        self.memoryLabel.setText("Memory:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.memoryLabel)
        self.memoryLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.memoryLineEdit.setObjectName("memoryLineEdit")
        self.memoryLineEdit.setPlaceholderText("300mb or 1gb")
        self.memoryLineEdit.setProperty("clearButtonEnabled", True)
        self.memoryLineEdit.setValidator(self.memoryValidator)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.memoryLineEdit)

        # 6 row
        self.scratchLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.scratchLabel.setObjectName("scratchLabel")
        self.scratchLabel.setText("Scratch:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.scratchLabel)
        self.scratchLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.scratchLineEdit.setObjectName("scratchLineEdit")
        self.scratchLineEdit.setPlaceholderText("150mb or 10gb:ssd")
        self.scratchLineEdit.setProperty("clearButtonEnabled", True)
        self.scratchLineEdit.setValidator(self.scratchValidator)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.scratchLineEdit)
