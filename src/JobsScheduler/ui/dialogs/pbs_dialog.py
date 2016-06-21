# -*- coding: utf-8 -*-
"""
Pbs dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets

from ui.data.preset_data import PbsPreset
from ui.data.queues import PbsQueues
from ui.dialogs.dialogs import UiFormDialog, AFormDialog
from ui.validators.validation import PbsNameValidator, WalltimeValidator, \
    MemoryValidator, ScratchValidator, ValidationColorizer


class PbsDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddPbsDialog",
                       windowTitle="Job Scheduler - Add PBS options",
                       title="Add PBS options",
                       subtitle="Please select details for PBS options.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditPbsDialog",
                        windowTitle="Job Scheduler - Edit PBS options",
                        title="Edit PBS options",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyPbsDialog",
                        windowTitle="Job Scheduler - Copy PBS options",
                        title="Copy PBS options",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent=None, excluded_names=None):
        super().__init__(parent)
        self.excluded_names = excluded_names

        # setup specific UI
        self.ui = UiPbsDialog()
        self.ui.setup_ui(self)

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)

        super()._connect_slots()

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
        return valid

    def get_data(self):
        preset = PbsPreset(name=self.ui.nameLineEdit.text())
        if self.ui.queueComboBox.currentText():
            preset.queue = self.ui.queueComboBox.currentText()
        if self.ui.walltimeLineEdit.text():
            preset.walltime = self.ui.walltimeLineEdit.text()
        preset.nodes = self.ui.nodesSpinBox.value()
        preset.ppn = self.ui.ppnSpinBox.value()
        if self.ui.memoryLineEdit.text():
            preset.memory = self.ui.memoryLineEdit.text()
        if self.ui.infinibandCheckbox.isChecked():
            preset.infiniband = True
        else:
            preset.infiniband = False
        return {
            'preset': preset,
            'old_name': self.old_name
        }

    def set_data(self, data=None, is_edit=False):
        # reset validation colors
        ValidationColorizer.colorize_white(self.ui.nameLineEdit)
        ValidationColorizer.colorize_white(self.ui.walltimeLineEdit)
        ValidationColorizer.colorize_white(self.ui.memoryLineEdit)

        if data:
            preset = data["preset"]
            self.old_name = preset.name
            if is_edit:
                try:
                    self.excluded_names.remove(preset.name)
                except ValueError:
                    pass
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.queueComboBox.setCurrentText(preset.queue)
            self.ui.walltimeLineEdit.setText(preset.walltime)
            self.ui.nodesSpinBox.setValue(preset.nodes)
            self.ui.ppnSpinBox.setValue(preset.ppn)
            self.ui.memoryLineEdit.setText(preset.memory)
            self.ui.infinibandCheckbox.setChecked(preset.infiniband)
        else:
            self.ui.nameLineEdit.clear()
            self.ui.queueComboBox.setCurrentIndex(-1)
            self.ui.walltimeLineEdit.clear()
            self.ui.nodesSpinBox.setValue(self.ui.nodesSpinBox.minimum())
            self.ui.ppnSpinBox.setValue(self.ui.ppnSpinBox.minimum())
            self.ui.memoryLineEdit.clear()
            self.ui.infinibandCheckbox.setChecked(False)


class UiPbsDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(400, 260)

        # validators
        self.nameValidator = PbsNameValidator(
            parent=self.mainVerticalLayoutWidget,
            excluded=dialog.excluded_names)
        self.walltimeValidator = WalltimeValidator(
            self.mainVerticalLayoutWidget)
        self.memoryValidator = MemoryValidator(
            self.mainVerticalLayoutWidget)
        self.scratchValidator = ScratchValidator(
            self.mainVerticalLayoutWidget)


        # form layout
        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setPlaceholderText("Name of the PBS options")
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
        self.nodesLabel.setText("Number of  Nodes:")
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
        self.ppnLabel.setText("Processes per Node:")
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
        self.infinibandLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.infinibandLabel.setObjectName("infinibandLabel")
        self.infinibandLabel.setText("Infiniband:")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.infinibandLabel)
        self.infinibandCheckbox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.infinibandCheckbox.setObjectName("infinibandCheckbox")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.infinibandCheckbox)

        return dialog
