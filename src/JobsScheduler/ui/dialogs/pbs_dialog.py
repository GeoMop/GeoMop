# -*- coding: utf-8 -*-
"""
Pbs dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets

from ui.data.preset_data import PbsPreset
from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import PresetNameValidator, WalltimeValidator, \
    MemoryValidator, ScratchValidator, ValidationColorizer


class PbsDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
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

    def __init__(self, parent=None):
        super().__init__(parent)
        # setup specific UI
        self.ui = UiPbsDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super()._connect_slots()
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
        key = self.ui.idLineEdit.text()
        preset = PbsPreset(self.ui.nameLineEdit.text())
        preset.queue = self.ui.queueComboBox.currentText()
        preset.walltime = self.ui.walltimeLineEdit.text()
        preset.nodes = self.ui.nodesSpinBox.value()
        preset.ppn = self.ui.ppnSpinBox.value()
        preset.memory = self.ui.memoryLineEdit.text()
        preset.scratch = self.ui.scratchLineEdit.text()
        return {
            "key": key,
            "preset": preset
        }

    def set_data(self, data=None):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)
        ValidationColorizer.colorize_white(self.ui.walltimeLineEdit)
        ValidationColorizer.colorize_white(self.ui.memoryLineEdit)
        ValidationColorizer.colorize_white(self.ui.scratchLineEdit)

        if data:
            key = data["key"]
            preset = data["preset"]
            self.ui.idLineEdit.setText(key)
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.queueComboBox.setCurrentText(preset.queue)
            self.ui.walltimeLineEdit.setText(preset.walltime)
            self.ui.nodesSpinBox.setValue(preset.nodes)
            self.ui.ppnSpinBox.setValue(preset.ppn)
            self.ui.memoryLineEdit.setText(preset.memory)
            self.ui.scratchLineEdit.setText(preset.scratch)
        else:
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            self.ui.queueComboBox.setCurrentIndex(-1)
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
        self.queueLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.queueLabel.setObjectName("queueLabel")
        self.queueLabel.setText("Queue:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.queueLabel)
        self.queueComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.queueComboBox.setObjectName(
            "queueComboBox")
        self.queueComboBox.setEditable(True)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.queueComboBox)
        
        # 3 row
        self.walltimeLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.walltimeLabel.setObjectName("walltimeLabel")
        self.walltimeLabel.setText("Walltime:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.walltimeLabel)
        self.walltimeLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.walltimeLineEdit.setObjectName("walltimeLineEdit")
        self.walltimeLineEdit.setPlaceholderText("1d4h or 20h")
        self.walltimeLineEdit.setProperty("clearButtonEnabled", True)
        self.walltimeLineEdit.setValidator(self.walltimeValidator)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.walltimeLineEdit)

        # 4 row
        self.nodesLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nodesLabel.setObjectName("nodesLabel")
        self.nodesLabel.setText("Specify number of nodes:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
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
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.nodesSpinBox)

        # 5 row
        self.ppnLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.ppnLabel.setObjectName("ppnLabel")
        self.ppnLabel.setText("Processors per Node:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
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
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.ppnSpinBox)

        # 6 row
        self.memoryLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.memoryLabel.setObjectName("walltimeLabel")
        self.memoryLabel.setText("Memory:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.memoryLabel)
        self.memoryLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.memoryLineEdit.setObjectName("memoryLineEdit")
        self.memoryLineEdit.setPlaceholderText("300mb or 1gb")
        self.memoryLineEdit.setProperty("clearButtonEnabled", True)
        self.memoryLineEdit.setValidator(self.memoryValidator)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.memoryLineEdit)

        # 7 row
        self.scratchLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.scratchLabel.setObjectName("scratchLabel")
        self.scratchLabel.setText("Scratch:")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.scratchLabel)
        self.scratchLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.scratchLineEdit.setObjectName("scratchLineEdit")
        self.scratchLineEdit.setPlaceholderText("150mb or 10gb:ssd")
        self.scratchLineEdit.setProperty("clearButtonEnabled", True)
        self.scratchLineEdit.setValidator(self.scratchValidator)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.scratchLineEdit)

        return dialog
