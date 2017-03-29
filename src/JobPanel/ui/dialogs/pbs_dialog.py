# -*- coding: utf-8 -*-
"""
Pbs dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtCore, QtWidgets

from helpers.importer import DialectImporter
from ui.data.preset_data import PbsPreset
from ui.dialogs.dialogs import AFormContainer
from ui.validators.validation import PresetsValidationColorizer


class PbsDialog(AFormContainer):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddPbsDialog",
                       windowTitle="Job Panel - Add PBS options",
                       title="Add PBS options",
                       subtitle="Please select details for PBS options.")

    PURPOSE_EDIT = dict(purposeType="PURPOSE_EDIT",
                        objectName="EditPbsDialog",
                        windowTitle="Job Panel - Edit PBS options",
                        title="Edit PBS options",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyPbsDialog",
                        windowTitle="Job Panel - Copy PBS options",
                        title="Copy PBS options",
                        subtitle="Change desired parameters and press SAVE to "
                                 "apply changes.")

    def __init__(self, parent, excluded_names):
        super().__init__(parent)
        
        self.excluded = {}
        self.excluded["name"]=excluded_names
        self.permitted = {}
        self.data = None
        
        # setup specific UI
        self.ui = UiPbsDialog()
        self.form = self.ui.setup_ui(parent)
        self.ui.validator.connect(self.valid)
        
        self.permitted['pbs_system'] = []        
        dialect_items = DialectImporter.get_available_dialects()
        for key in dialect_items:
            self.ui.pbsSystemComboBox.addItem(dialect_items[key], key)
            self.permitted['pbs_system'].append(key)
        
        self.preset = None

    def first_focus(self):
        """
        Get focus to first property
        """
        self.ui.nameLineEdit.setFocus()
        
    def is_dirty(self):        
        """return if data was changes"""
        if self.preset is None:
            return True
        if self.old_name!=self.ui.nameLineEdit.text():
            return True
        p = self.get_data()['preset']
        if self.preset.pbs_system!=p.pbs_system:
            return True
        if self.preset.queue!=p.queue:
            return True
        if self.preset.walltime!=p.walltime:
            return True
        if self.preset.nodes!=p.nodes:
            return True
        if self.preset.ppn!=p.ppn:
            return True
        if self.preset.memory!=p.memory:
            return True
        if p.infiniband != self.preset.infiniband:
            return True
        return False

    def get_data(self):        
        preset = PbsPreset(name=self.ui.nameLineEdit.text())
        if self.ui.pbsSystemComboBox.currentText():
            preset.pbs_system = self.ui.pbsSystemComboBox.currentData()
        if self.ui.queueComboBox.currentText():
            preset.queue = self.ui.queueComboBox.currentText()
        if self.ui.walltimeLineEdit.text():
            preset.walltime = self.ui.walltimeLineEdit.text()
        else:
            preset.walltime = ''
        preset.nodes = self.ui.nodesSpinBox.value()
        preset.ppn = self.ui.ppnSpinBox.value()
        if self.ui.memoryLineEdit.text():
            preset.memory = self.ui.memoryLineEdit.text()
        else:
            preset.memory = ''
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
        self.ui.validator.reset_colorize()
        
        if data:
            preset = data["preset"]
            self.preset = preset
            self.old_name = preset.name
            if is_edit:
                try:
                    self.excluded["name"].remove(preset.name)
                except ValueError:
                    pass
            self.ui.pbsSystemComboBox.setCurrentIndex(
                self.ui.pbsSystemComboBox.findData(preset.pbs_system))
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.queueComboBox.setCurrentText(preset.queue)
            self.ui.walltimeLineEdit.setText(preset.walltime)
            self.ui.nodesSpinBox.setValue(preset.nodes)
            self.ui.ppnSpinBox.setValue(preset.ppn)
            self.ui.memoryLineEdit.setText(preset.memory)
            self.ui.infinibandCheckbox.setChecked(preset.infiniband)
            self.valid()
        else:
            self.ui.nameLineEdit.clear()
            dialect_items = DialectImporter.get_available_dialects()
            if len(dialect_items)==0:
                self.ui.pbsSystemComboBox.setCurrentIndex(-1)
            else:
                self.ui.pbsSystemComboBox.setCurrentIndex(0)
            self.ui.queueComboBox.setCurrentIndex(-1)
            self.ui.walltimeLineEdit.clear()
            self.ui.nodesSpinBox.setValue(self.ui.nodesSpinBox.minimum())
            self.ui.ppnSpinBox.setValue(self.ui.ppnSpinBox.minimum())
            self.ui.memoryLineEdit.clear()
            self.ui.infinibandCheckbox.setChecked(False)


class UiPbsDialog():
    """
    UI extensions of form dialog.
    """

    def setup_ui(self, dialog):
        self.validator = PresetsValidationColorizer()
        
        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)

        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setContentsMargins(10, 15, 10, 15)

        # form layout
        # 1 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setPlaceholderText("Name of the PBS options")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.validator.add('name',self.nameLineEdit)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # 2 row
        self.pbsSystemLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.pbsSystemLabel.setText("PBS System:")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole,
                                  self.pbsSystemLabel)
        self.pbsSystemComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.validator.add('pbs_system',self.nameLineEdit)         
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole,
                                  self.pbsSystemComboBox)
        
        # 3 row
        self.queueLabel = QtWidgets.QLabel(
            self.mainVerticalLayoutWidget)
        self.queueLabel.setText("Queue:")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.queueLabel)
        self.queueComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.queueComboBox.setEditable(True)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole,
                                  self.queueComboBox)
        
        # 4 row
        self.walltimeLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.walltimeLabel.setText("Walltime:")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.walltimeLabel)
        self.walltimeLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.walltimeLineEdit.setPlaceholderText("1d4h or 20h")
        self.walltimeLineEdit.setProperty("clearButtonEnabled", True)
        self.validator.add('walltime',self.walltimeLineEdit)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.walltimeLineEdit)

        # 5 row
        self.nodesLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nodesLabel.setText("Number of  Nodes:")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.nodesLabel)
        self.nodesSpinBox = QtWidgets.QSpinBox(
            self.mainVerticalLayoutWidget)
        self.nodesSpinBox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.nodesSpinBox.setMinimum(1)
        self.nodesSpinBox.setMaximum(1000)
        self.nodesSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt
            .AlignVCenter)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.nodesSpinBox)

        # 6 row
        self.ppnLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.ppnLabel.setText("Processes per Node:")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole,
                                  self.ppnLabel)
        self.ppnSpinBox = QtWidgets.QSpinBox(
            self.mainVerticalLayoutWidget)
        self.ppnSpinBox.setButtonSymbols(
            QtWidgets.QAbstractSpinBox.PlusMinus)
        self.ppnSpinBox.setMinimum(1)
        self.ppnSpinBox.setMaximum(100)
        self.ppnSpinBox.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt
            .AlignVCenter)
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole,
                                  self.ppnSpinBox)

        # 7 row
        self.memoryLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.memoryLabel.setText("Memory:")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.memoryLabel)
        self.memoryLineEdit = QtWidgets.QLineEdit(
            self.mainVerticalLayoutWidget)
        self.memoryLineEdit.setPlaceholderText("300mb or 1gb")
        self.memoryLineEdit.setProperty("clearButtonEnabled", True)        
        self.validator.add('memory',self.memoryLineEdit)
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole,
                                  self.memoryLineEdit)

        # 8 row
        self.infinibandLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.infinibandLabel.setText("Infiniband:")
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole,
                                  self.infinibandLabel)
        self.infinibandCheckbox = QtWidgets.QCheckBox(
            self.mainVerticalLayoutWidget)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole,
                                  self.infinibandCheckbox)

        return self.formLayout
