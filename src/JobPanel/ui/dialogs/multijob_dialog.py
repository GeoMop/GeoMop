# -*- coding: utf-8 -*-
"""
Multijob dialog
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

import logging
import copy

from PyQt5 import QtCore, QtWidgets, QtGui
from JobPanel.ui.data.mj_data import MultiJobPreset
from JobPanel.ui.data.preset_data import PbsPreset
from JobPanel.ui.dialogs.dialogs import UiFormDialog, AFormDialog
from gm_base.geomop_analysis import Analysis, InvalidAnalysis
from JobPanel.ui.validators.validation import PresetsValidationColorizer
from gm_base import icon


class PbsComboBox(QtWidgets.QComboBox):
    """Modified QComboBox for PBS options purposes."""
    focusOut = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self._temp_text = ""

        self.setEditable(True)

        self.editTextChanged.connect(self._save_temp_text)

    def focusOutEvent(self, event):
        self.focusOut.emit(self._temp_text)

        super().focusOutEvent(event)

    def _save_temp_text(self, text):
        self._temp_text = text


class PbsPresetsValidationColorizer(PresetsValidationColorizer):
    """Modified colorizer for PBS options purposes."""
    def colorize(self, errors):
        ret = super().colorize(errors)

        for key, control in self.controls.items():
            if key in errors:
                if not isinstance(control, PbsComboBox):
                    control.setFocus()

        return ret

    def connect(self, edited_func, finished_func):
        for key, control in self.controls.items():
            if isinstance(control, QtWidgets.QLineEdit):
                control.textChanged.connect(edited_func)
                control.editingFinished.connect(finished_func)
            elif isinstance(control, QtWidgets.QSpinBox):
                control.valueChanged.connect(edited_func)
                control.editingFinished.connect(finished_func)
            elif isinstance(control, QtWidgets.QComboBox):
                if not isinstance(control, PbsComboBox):
                    control.currentIndexChanged.connect(finished_func)
            elif isinstance(control, QtWidgets.QCheckBox):
                control.stateChanged.connect(finished_func)


class MultiJobDialog(AFormDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    # purposes of dialog by action
    PURPOSE_ADD = dict(purposeType="PURPOSE_ADD",
                       objectName="AddMultiJobDialog",
                       windowTitle="Job Panel - Add MultiJob",
                       title="Add MultiJob",
                       subtitle="Please select details to schedule set of "
                                "tasks\nfor computation and press Run to "
                                 "start multijob.")

    PURPOSE_COPY = dict(purposeType="PURPOSE_COPY",
                        objectName="CopyMultiJobDialog",
                        windowTitle="Job Panel - Copy MultiJob",
                        title="Copy MultiJob",
                        subtitle="Change desired parameters and press Run to "
                                 "start multijob.\n")

    PURPOSE_COPY_PREFIX = "Copy_of"

    def __init__(self, parent=None, data=None):
        super().__init__(parent)

        self.excluded = {"name": []}
        self.permitted = {}

        # setup specific UI
        self.ui = UiMultiJobDialog()
        self.ui.setup_ui(self)
        self.ui.validator.connect(self.valid)
        self.data = data

        self._from_mj = None

        self.preset = None
        self.pbs = data.pbs_presets
        self.ssh = data.ssh_presets

        self._preferred_mj_pbs = ""
        self._preferred_j_pbs = ""

        # preset purpose
        self.set_purpose(self.PURPOSE_ADD)
        self.set_analyses(data.workspaces)
        self.set_ssh_presets()
        self.set_pbs_presets()

        self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Save).setText("Run")

        # connect slots
        # connect generic presets slots (must be called after UI setup)
        super()._connect_slots()
        self.ui.analysisComboBox.currentIndexChanged.connect(self.update_mj_name)
        self.ui.multiJobSshPresetComboBox.currentIndexChanged.connect(self._handle_mj_ssh_changed)
        self.ui.jobSshPresetComboBox.currentIndexChanged.connect(self._handle_j_ssh_changed)
        self.ui.multiJobPbsPresetComboBox.currentIndexChanged.connect(self._handle_mj_pbs_changed)
        self.ui.jobPbsPresetComboBox.currentIndexChanged.connect(self._handle_j_pbs_changed)

        # PBS options
        #############

        self.pbs_block_signals(True)

        self.pbs_old_name = None
        self.pbs_presets_changed = False
        """True if pbs presets must be saved"""

        self.pbs_excluded = {"name": []}
        self.pbs_permitted = {}

        self.ui.pbs_AddButton.clicked.connect(self._handle_pbs_AddButton)
        self.ui.pbs_RemoveButton.clicked.connect(self._handle_pbs_RemoveButton)
        self.ui.pbs_validator.connect(self.pbs_edited, self.pbs_editing_finished)
        self.ui.pbs_nameComboBox.activated[str].connect(self._handle_pbs_name_activated)
        self.ui.pbs_nameComboBox.editTextChanged.connect(self.pbs_edited)
        self.ui.pbs_nameComboBox.focusOut.connect(self._handle_pbs_name_focus_out)

        self.pbs_permitted['pbs_system'] = []
        # dialect_items = DialectImporter.get_available_dialects()
        dialect_items = {"PbsDialectPBSPro": "PBSPro"}
        for key in dialect_items:
            self.ui.pbs_pbsSystemComboBox.addItem(dialect_items[key], key)
            self.pbs_permitted['pbs_system'].append(key)

        self.pbs_preset = None

        self.pbs_show_pbs()

    def accept(self):
        self.pbs_save()
        super().accept()

    def reject(self):
        self.pbs_save()
        super().reject()

    def update_mj_name(self):
        analysis_name = self.ui.analysisComboBox.currentText()
        try:
            counter = Analysis.open(self.data.workspaces.get_path(), analysis_name).mj_counter
        except InvalidAnalysis:
            counter = 1
        name = self.ui.multiJobSshPresetComboBox.currentText() + '_' + str(counter)
        self.ui.nameLineEdit.setText(name)
        self.valid()

    def valid(self):
        preset = self.get_data()["preset"]

        # excluded names
        self.excluded["name"] = []
        if self.data.multijobs:
            prefix = preset.analysis + "_"
            prefix_len = len(prefix)
            self.excluded["name"] = [k[prefix_len:] for k in self.data.multijobs.keys() if k.startswith(prefix)]

        errors = preset.validate(self.excluded, self.permitted)
        self.ui.validator.colorize(errors)
        return len(errors)==0

    def _handle_mj_ssh_changed(self, index):
        key = self.ui.multiJobSshPresetComboBox.currentText()
        if key == "" or key == UiMultiJobDialog.SSH_LOCAL_EXEC or self.ssh[key].pbs_system == '':
            self.ui.multiJobPbsPresetComboBox.setEnabled(False)
        else:
            self._enable_pbs(self.ui.multiJobPbsPresetComboBox, key)
        self.update_mj_name()
        self._handle_j_ssh_changed()

    def _enable_pbs(self, combo, key):
        """Enable all pbs presets with same sytems as is in choosed ssh preset"""
        combo.setEnabled(True)
        model = combo.model()
        if not key in self.ssh:
            system = ''
        else:
            system = self.ssh[key].pbs_system
        reselect = False
        curr = combo.currentIndex()
        for i in range(0, combo.count()):
            item = model.item(i)
            if not item.text() in self.pbs:
                continue
            pbs_system = self.pbs[item.text()].pbs_system
            disable = pbs_system is None or system != pbs_system
            if disable:
                item.setFlags(item.flags() & ~(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled))
                item.setData(combo.palette().color(
                    QtGui.QPalette.Disabled, QtGui.QPalette.Text), QtCore.Qt.TextColorRole)
                if curr == i:
                    reselect = True
            else:
                item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled);
                item.setData(QtCore.QVariant(), QtCore.Qt.TextColorRole)
        if reselect:
            combo.setCurrentIndex(0)

        combo.blockSignals(False)

    def _handle_j_ssh_changed(self, index=0):
        key = self.ui.jobSshPresetComboBox.currentText()
        if key == UiMultiJobDialog.SSH_LOCAL_EXEC:
            # get server pbs
            key = self.ui.multiJobSshPresetComboBox.currentText()
            if key == '' or key == UiMultiJobDialog.SSH_LOCAL_EXEC or self.ssh[key].pbs_system == '':
                self.ui.jobPbsPresetComboBox.setEnabled(False)
            else:
                self._enable_pbs(self.ui.jobPbsPresetComboBox, key)

        elif key in self.ssh and self.ssh[key].pbs_system == '':
            self.ui.jobPbsPresetComboBox.setEnabled(False)
        else:
            self._enable_pbs(self.ui.jobPbsPresetComboBox, key)

    def _handle_mj_pbs_changed(self):
        key = self.ui.multiJobPbsPresetComboBox.currentText()
        self._preferred_mj_pbs = key
        self.pbs_show_pbs(key)

    def _handle_j_pbs_changed(self):
        key = self.ui.jobPbsPresetComboBox.currentText()
        self._preferred_j_pbs = key
        self.pbs_show_pbs(key)

    def set_analyses(self, config):
        self.ui.analysisComboBox.clear()        
        if config is not None:
            path = config.get_path()
            if path is not None:
                for analysis_name in Analysis.list_analyses_in_workspace(path):
                    self.ui.analysisComboBox.addItem(analysis_name, analysis_name)
        if self.ui.analysisComboBox.count()==0:            
            self.ui.analysisComboBox.addItem('')
        self.ui.analysisComboBox.model().sort(0)

    def set_pbs_presets(self):
        self.ui.multiJobPbsPresetComboBox.blockSignals(True)
        self.ui.jobPbsPresetComboBox.blockSignals(True)

        self.ui.multiJobPbsPresetComboBox.clear()
        self.ui.jobPbsPresetComboBox.clear()

        # add default PBS options (none)
        self.ui.multiJobPbsPresetComboBox.addItem(self.ui.PBS_OPTION_NONE, self.ui.PBS_OPTION_NONE)
        self.ui.jobPbsPresetComboBox.addItem(self.ui.PBS_OPTION_NONE, self.ui.PBS_OPTION_NONE)

        self.permitted['mj_pbs_preset'] = []
        self.permitted['mj_pbs_preset'].append(None)
        self.permitted['j_pbs_preset'] = []
        self.permitted['j_pbs_preset'].append(None)

        if self.pbs:
            keys = sorted(self.pbs.keys(), key=lambda k: self.pbs[k].name)
            for key in keys:
                self.ui.multiJobPbsPresetComboBox.addItem(self.pbs[key].name, key)
                self.ui.jobPbsPresetComboBox.addItem(self.pbs[key].name, key)
                self.permitted['mj_pbs_preset'].append(key)
                self.permitted['j_pbs_preset'].append(key)

            if len(self._preferred_mj_pbs) > 0:
                ind = self.ui.multiJobPbsPresetComboBox.findData(self._preferred_mj_pbs)
                if ind >= 0:
                    self.ui.multiJobPbsPresetComboBox.setCurrentIndex(ind)
            if len(self._preferred_j_pbs) > 0:
                ind = self.ui.jobPbsPresetComboBox.findData(self._preferred_j_pbs)
                if ind >= 0:
                    self.ui.jobPbsPresetComboBox.setCurrentIndex(ind)
            self._handle_mj_ssh_changed(0)
            self._handle_j_ssh_changed(0)

        self.ui.multiJobPbsPresetComboBox.blockSignals(False)
        self.ui.jobPbsPresetComboBox.blockSignals(False)

    def set_ssh_presets(self):
        self.ui.multiJobSshPresetComboBox.clear()
        self.ui.jobSshPresetComboBox.clear()

        # add default SSH option for local execution
        self.ui.multiJobSshPresetComboBox.addItem(self.ui.SSH_LOCAL_EXEC, self.ui.SSH_LOCAL_EXEC)
        self.ui.jobSshPresetComboBox.addItem(self.ui.SSH_LOCAL_EXEC, self.ui.SSH_LOCAL_EXEC)

        self.permitted['mj_ssh_preset'] = []
        self.permitted['mj_ssh_preset'].append(None)
        self.permitted['j_ssh_preset'] = []
        self.permitted['j_ssh_preset'].append(None)

        # Currently is for Job SSH host supported only "local", therefore others are commented out
        if self.ssh:
            keys = sorted(self.ssh.keys(), key=lambda k: self.ssh[k].name)
            for key in keys:
                self.ui.multiJobSshPresetComboBox.addItem(self.ssh[key].name, key)
                #self.ui.jobSshPresetComboBox.addItem(self.ssh[key].name, key)
                if self.ssh[key].tested:
                    self.permitted['mj_ssh_preset'].append(key)
                    #self.permitted['j_ssh_preset'].append(key)
                else:
                    model = self.ui.multiJobSshPresetComboBox.model()
                    item = model.item(self.ui.multiJobSshPresetComboBox.count() - 1)
                    item.setFlags(item.flags() & ~(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled))
                    # model = self.ui.jobSshPresetComboBox.model()
                    # item = model.item(self.ui.jobSshPresetComboBox.count() - 1)
                    # item.setFlags(item.flags() & ~(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled))
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(
                self.ui.multiJobSshPresetComboBox.findData(
                    'local' if self.preset is None or self.preset.mj_ssh_preset is None or
                               self.preset.mj_ssh_preset not in self.permitted['mj_ssh_preset']
                        else self.preset.mj_ssh_preset))
            # self.ui.jobSshPresetComboBox.setCurrentIndex(
            #     self.ui.jobSshPresetComboBox.findData(
            #         'local' if self.preset is None or self.preset.j_ssh_preset is None or
            #                    self.preset.j_ssh_preset not in self.permitted['j_ssh_preset']
            #             else self.preset.j_ssh_preset))

    def get_data(self):
        key = self.ui.idLineEdit.text()
        preset = MultiJobPreset(name=self.ui.nameLineEdit.text())

        if self.ui.multiJobSshPresetComboBox.currentText() != UiMultiJobDialog.SSH_LOCAL_EXEC:
            if self.ui.multiJobSshPresetComboBox.currentIndex() == -1:
                preset.mj_ssh_preset = ""
            else:
                preset.mj_ssh_preset = self.ui.multiJobSshPresetComboBox.currentData()
        preset.mj_execution_type = UiMultiJobDialog.DELEGATOR_LABEL

        if self.ui.multiJobSshPresetComboBox.currentText() == UiMultiJobDialog.SSH_LOCAL_EXEC:
            preset.mj_execution_type = UiMultiJobDialog.EXEC_LABEL
        elif self.ui.multiJobPbsPresetComboBox.currentText() == UiMultiJobDialog.PBS_OPTION_NONE:
            preset.mj_remote_execution_type = UiMultiJobDialog.EXEC_LABEL
        else:
            preset.mj_remote_execution_type = UiMultiJobDialog.PBS_LABEL
        if self.ui.multiJobPbsPresetComboBox.isEnabled() and \
                self.ui.multiJobPbsPresetComboBox.currentIndex() != 0:
            if self.ui.jobPbsPresetComboBox.currentIndex() == -1:
                preset.mj_pbs_preset = ""
            else:
                preset.mj_pbs_preset =\
                    self.ui.multiJobPbsPresetComboBox.currentData()
            if preset.mj_pbs_preset is None:
                preset.mj_pbs_preset = ""

        if self.ui.jobSshPresetComboBox.currentText() != UiMultiJobDialog.SSH_LOCAL_EXEC:
            if self.ui.jobSshPresetComboBox.currentIndex() == -1:
                preset.j_ssh_preset = ""
            else:
                preset.j_ssh_preset = self.ui.jobSshPresetComboBox.currentData()

        preset.j_execution_type = UiMultiJobDialog.REMOTE_LABEL
        if self.ui.jobSshPresetComboBox.currentText() == UiMultiJobDialog.SSH_LOCAL_EXEC:
            if self.ui.jobPbsPresetComboBox.currentText() == UiMultiJobDialog.PBS_OPTION_NONE:
                preset.j_execution_type = UiMultiJobDialog.EXEC_LABEL
            else:
                preset.j_execution_type = UiMultiJobDialog.PBS_LABEL
        elif self.ui.jobPbsPresetComboBox.currentText() == UiMultiJobDialog.PBS_OPTION_NONE:
            preset.j_remote_execution_type = UiMultiJobDialog.EXEC_LABEL
        else:
            preset.j_remote_execution_type = UiMultiJobDialog.PBS_LABEL

        if self.ui.jobPbsPresetComboBox.isEnabled() and \
                self.ui.jobPbsPresetComboBox.currentIndex() != 0:
            if self.ui.jobPbsPresetComboBox.currentIndex() == -1:
                preset.j_pbs_preset = ""
            else:
                preset.j_pbs_preset = self.ui.jobPbsPresetComboBox.currentData()

        preset.log_level = self.ui.logLevelComboBox.currentData()
        preset.analysis = self.ui.analysisComboBox.currentText()
        preset.from_mj = self._from_mj
        return {
            "key": key,
            "preset": preset
        }

    def set_data(self, data=None, is_edit=False):
        # reset validation colors
        self.ui.validator.reset_colorize()
        if data:
            key = data["key"]
            preset = data["preset"]
            self.preset = preset
            self._from_mj = preset.from_mj
            self.ui.idLineEdit.setText(key)
            self.ui.nameLineEdit.setText(preset.name)
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(
                self.ui.multiJobSshPresetComboBox.findData(
                    'local' if preset.mj_ssh_preset is None else preset.mj_ssh_preset))
            self._preferred_mj_pbs = 'no PBS' if preset.mj_pbs_preset is None else preset.mj_pbs_preset
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(
                self.ui.multiJobPbsPresetComboBox.findData(
                    self._preferred_mj_pbs))

            self.ui.jobSshPresetComboBox.setCurrentIndex(
                self.ui.jobSshPresetComboBox.findData(
                    'local' if preset.j_ssh_preset is None else preset.j_ssh_preset))
            self._preferred_j_pbs = 'no PBS' if preset.j_pbs_preset is None else preset.j_pbs_preset
            self.ui.jobPbsPresetComboBox.setCurrentIndex(
                self.ui.jobPbsPresetComboBox.findData(
                    self._preferred_j_pbs))
            self.ui.logLevelComboBox.setCurrentIndex(
                self.ui.logLevelComboBox.findData(preset.log_level))
            self.ui.analysisComboBox.setCurrentIndex(
                self.ui.analysisComboBox.findData(preset.analysis))
            if self._from_mj is not None:
                self.ui.analysisComboBox.setDisabled(True)
            self._handle_mj_ssh_changed(0)
            self._handle_j_ssh_changed(0)
            self.valid()
        else:
            self.ui.analysisComboBox.setEnabled(True)
            self.ui.idLineEdit.clear()
            self.ui.nameLineEdit.clear()
            #self.ui.resourceComboBox.setCurrentIndex(0)
            self.ui.multiJobSshPresetComboBox.setCurrentIndex(0)
            self.ui.multiJobPbsPresetComboBox.setCurrentIndex(0)
            self.ui.jobPbsPresetComboBox.setCurrentIndex(0)
            self.ui.analysisComboBox.setCurrentIndex(0)
            self.ui.logLevelComboBox.setCurrentIndex(1)

            self.update_mj_name()

    # PBS options
    #############

    def _handle_pbs_AddButton(self):
        # new preset name
        name = "new"
        if name in self.pbs:
            ind = 1
            while True:
                name = "new_{}".format(ind)
                if name not in self.pbs:
                    break
                ind += 1

        # new preset
        dialect_items = {"PbsDialectPBSPro": "PBSPro"}
        preset = PbsPreset(
            name=name,
            pbs_system=list(dialect_items.keys())[0],
            queue="",
            walltime="",
            nodes=1,
            ppn=1,
            memory="",
            infiniband=False
        )

        self.pbs[preset.name] = preset
        self.pbs_preset = preset
        self.pbs_presets_changed = True

        self.pbs_show_pbs(preset.name)
        self.ui.pbs_nameComboBox.setFocus()
        self.ui.pbs_nameComboBox.lineEdit().selectAll()

        self.set_pbs_presets()

    def _handle_pbs_RemoveButton(self):
        key = self.pbs_old_name
        if key in self.pbs:
            del self.pbs[key]
            self.pbs_presets_changed = True
            self.set_pbs_presets()
        self.pbs_show_pbs()
        self.set_pbs_presets()

    def _handle_pbs_name_activated(self, text):
        self.pbs_show_pbs(text)
        self.set_pbs_presets()

    def _handle_pbs_name_focus_out(self, text):
        if text != self.pbs_old_name:
            if (text in self.pbs) or (not self.pbs_valid()):
                self.ui.pbs_nameComboBox.setEditText(self.pbs_old_name)
            else:
                self.pbs_editing_finished()

    def pbs_is_dirty(self):
        """return if data was changes"""
        if self.pbs_preset is None:
            return True
        if self.pbs_old_name!=self.ui.pbs_nameComboBox.currentText():
            return True
        p = self.pbs_get_data()['preset']
        if self.pbs_preset.pbs_system!=p.pbs_system:
            return True
        if self.pbs_preset.queue!=p.queue:
            return True
        if self.pbs_preset.walltime!=p.walltime:
            return True
        if self.pbs_preset.nodes!=p.nodes:
            return True
        if self.pbs_preset.ppn!=p.ppn:
            return True
        if self.pbs_preset.memory!=p.memory:
            return True
        if p.infiniband != self.pbs_preset.infiniband:
            return True
        return False

    def pbs_get_data(self):
        preset = PbsPreset(name=self.ui.pbs_nameComboBox.currentText())
        if self.ui.pbs_pbsSystemComboBox.currentText():
            preset.pbs_system = self.ui.pbs_pbsSystemComboBox.currentData()
        if self.ui.pbs_queueLineEdit.text():
            preset.queue = self.ui.pbs_queueLineEdit.text()
        else:
            preset.queue = ''
        if self.ui.pbs_walltimeLineEdit.text():
            preset.walltime = self.ui.pbs_walltimeLineEdit.text()
        else:
            preset.walltime = ''
        preset.nodes = self.ui.pbs_nodesSpinBox.value()
        preset.ppn = self.ui.pbs_ppnSpinBox.value()
        if self.ui.pbs_memoryLineEdit.text():
            preset.memory = self.ui.pbs_memoryLineEdit.text()
        else:
            preset.memory = ''
        if self.ui.pbs_infinibandCheckBox.isChecked():
            preset.infiniband = True
        else:
            preset.infiniband = False
        return {
            'preset': preset,
            'old_name': self.pbs_old_name
        }

    def pbs_set_data(self, data=None):
        # reset validation colors
        self.ui.pbs_validator.reset_colorize()

        if data:
            preset = data["preset"]
            self.pbs_preset = preset
            self.pbs_old_name = preset.name

            self.ui.pbs_pbsSystemComboBox.setCurrentIndex(
                self.ui.pbs_pbsSystemComboBox.findData(preset.pbs_system))
            self.ui.pbs_nameComboBox.setCurrentText(preset.name)
            self.ui.pbs_queueLineEdit.setText(preset.queue)
            self.ui.pbs_walltimeLineEdit.setText(preset.walltime)
            self.ui.pbs_nodesSpinBox.setValue(preset.nodes)
            self.ui.pbs_ppnSpinBox.setValue(preset.ppn)
            self.ui.pbs_memoryLineEdit.setText(preset.memory)
            self.ui.pbs_infinibandCheckBox.setChecked(preset.infiniband)
            self.pbs_valid()
        else:
            self.ui.pbs_nameComboBox.clear()
            # dialect_items = DialectImporter.get_available_dialects()
            dialect_items = {"PbsDialectPBSPro": "PBSPro"}
            if len(dialect_items) == 0:
                self.ui.pbs_pbsSystemComboBox.setCurrentIndex(-1)
            else:
                self.ui.pbs_pbsSystemComboBox.setCurrentIndex(0)
            self.ui.pbs_queueLineEdit.clear()
            self.ui.pbs_walltimeLineEdit.clear()
            self.ui.pbs_nodesSpinBox.setValue(self.ui.pbs_nodesSpinBox.minimum())
            self.ui.pbs_ppnSpinBox.setValue(self.ui.pbs_ppnSpinBox.minimum())
            self.ui.pbs_memoryLineEdit.clear()
            self.ui.pbs_infinibandCheckBox.setChecked(False)

    def pbs_valid(self):
        data = self.pbs_get_data()

        # excluded names
        self.pbs_excluded["name"] = [p.name for p in self.pbs.values() if p.name != self.pbs_old_name]

        errors = data['preset'].validate(self.pbs_excluded, self.pbs_permitted)
        self.ui.pbs_validator.colorize(errors)
        return len(errors) == 0

    def pbs_enable(self, enable=True):
        self.ui.pbs_nameComboBox.setEnabled(enable)
        self.ui.pbs_pbsSystemComboBox.setEnabled(enable)
        self.ui.pbs_queueLineEdit.setEnabled(enable)
        self.ui.pbs_walltimeLineEdit.setEnabled(enable)
        self.ui.pbs_nodesSpinBox.setEnabled(enable)
        self.ui.pbs_ppnSpinBox.setEnabled(enable)
        self.ui.pbs_memoryLineEdit.setEnabled(enable)
        self.ui.pbs_infinibandCheckBox.setEnabled(enable)

        self.ui.pbs_RemoveButton.setEnabled(enable)

    def pbs_block_signals(self, enable=True):
        self.ui.pbs_nameComboBox.blockSignals(enable)
        self.ui.pbs_pbsSystemComboBox.blockSignals(enable)
        self.ui.pbs_queueLineEdit.blockSignals(enable)
        self.ui.pbs_walltimeLineEdit.blockSignals(enable)
        self.ui.pbs_nodesSpinBox.blockSignals(enable)
        self.ui.pbs_ppnSpinBox.blockSignals(enable)
        self.ui.pbs_memoryLineEdit.blockSignals(enable)
        self.ui.pbs_infinibandCheckBox.blockSignals(enable)

        # ClearButton workaround
        if not enable:
            self.ui.pbs_queueLineEdit.textChanged.emit(self.ui.pbs_queueLineEdit.text())
            self.ui.pbs_walltimeLineEdit.textChanged.emit(self.ui.pbs_walltimeLineEdit.text())
            self.ui.pbs_memoryLineEdit.textChanged.emit(self.ui.pbs_memoryLineEdit.text())

    def pbs_edited(self):
        self.pbs_valid()

    def pbs_editing_finished(self):
        if self.pbs_valid():
            if self.pbs_is_dirty():
                # update presets
                data = self.pbs_get_data()
                del self.pbs[data['old_name']]
                preset = copy.deepcopy(data['preset'])
                self.pbs[preset.name] = preset

                if self._preferred_mj_pbs == self.pbs_old_name:
                    self._preferred_mj_pbs = preset.name
                if self._preferred_j_pbs == self.pbs_old_name:
                    self._preferred_j_pbs = preset.name

                self.pbs_preset = preset
                self.pbs_old_name = preset.name

                self.pbs_presets_changed = True

                self.pbs_show_pbs(preset.name)
                self.set_pbs_presets()

    def pbs_show_pbs(self, preferred_pbs=None):
        self.pbs_block_signals(True)

        self.ui.pbs_nameComboBox.clear()

        if len(self.pbs) > 0:
            for key in self.pbs.keys():
                self.ui.pbs_nameComboBox.addItem(key)
            self.ui.pbs_nameComboBox.model().sort(0)

            if (preferred_pbs is not None) and (preferred_pbs in self.pbs):
                key = preferred_pbs
            else:
                key = list(self.pbs.keys())[0]

            preset = copy.deepcopy(self.pbs[key])
            data = {
                "preset": preset
            }
            self.pbs_set_data(data)

            self.pbs_enable(True)
            self.pbs_block_signals(False)
        else:
            self.pbs_set_data()
            self.pbs_enable(False)

    def pbs_save(self):
        """Saves PBS options if needed."""
        if self.pbs_presets_changed:
            self.pbs.save()
            self.pbs_presets_changed = False


class UiMultiJobDialog(UiFormDialog):
    """
    UI extensions of form dialog.
    """
    EXECUTE_USING_LABEL = "Execute using:"
    EXECUTION_TYPE_LABEL = "Execution type:"
    SSH_PRESET_LABEL = "SSH host:"
    PBS_PRESET_LABEL = "PBS options:"
    JOB_ENV_LABEL = "Job environment:"

    EXEC_LABEL = "EXEC"
    DELEGATOR_LABEL = "DELEGATOR"
    REMOTE_LABEL = "REMOTE"
    PBS_LABEL = "PBS"
    SSH_LOCAL_EXEC = "local"
    PBS_OPTION_NONE = "no PBS"

    def setup_ui(self, dialog):
        # dialog properties
        dialog.setObjectName("FormDialog")
        dialog.setWindowTitle("Form dialog")
        dialog.setModal(True)

        # main dialog layout
        self.mainVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.mainVerticalLayout = QtWidgets.QVBoxLayout(self.mainVerticalLayoutWidget)

        # labels
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum,
                                           QtWidgets.QSizePolicy.Maximum)

        # title label
        self.titleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        titleFont = QtGui.QFont()
        titleFont.setPointSize(15)
        titleFont.setBold(True)
        titleFont.setWeight(75)
        self.titleLabel.setFont(titleFont)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setText("Title")
        self.titleLabel.setSizePolicy(sizePolicy)
        # self.titleLabel.setWordWrap(True)
        self.mainVerticalLayout.addWidget(self.titleLabel)

        # subtitle label
        #self.subtitleLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.subtitleLabel = QtWidgets.QLabel()
        subtitleFont = QtGui.QFont()
        subtitleFont.setWeight(50)
        self.subtitleLabel.setFont(subtitleFont)
        self.subtitleLabel.setObjectName("subtitleLabel")
        self.subtitleLabel.setText("Subtitle text")
        self.subtitleLabel.setSizePolicy(sizePolicy)
        # self.subtitleLabel.setWordWrap(True)
        #self.mainVerticalLayout.addWidget(self.subtitleLabel)

        # divider
        self.headerDivider = QtWidgets.QFrame(self.mainVerticalLayoutWidget)
        self.headerDivider.setObjectName("headerDivider")
        self.headerDivider.setFrameShape(QtWidgets.QFrame.HLine)
        self.headerDivider.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.mainVerticalLayout.addWidget(self.headerDivider)

        # form layout
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.formLayout.setContentsMargins(0, 5, 0, 5)

        # add form to main layout
        self.mainVerticalLayout.addLayout(self.formLayout)

        # button box (order of of buttons is set by system default)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.mainVerticalLayoutWidget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close | QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.mainVerticalLayout.addWidget(self.buttonBox)


        # dialog properties
        dialog.resize(900, 440)

        # validators
        self.validator = PresetsValidationColorizer()

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
        self.analysisLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.analysisLabel.setObjectName("analysisLabel")
        self.analysisLabel.setText("Analysis:")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole,
                                  self.analysisLabel)
        self.analysisComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.analysisComboBox.setObjectName("analysisComboBox")
        self.validator.add('analysis', self.analysisComboBox)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole,
                                  self.analysisComboBox)

        # separator
        sep = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        sep.setText("")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, sep)

        # font
        labelFont = QtGui.QFont()
        labelFont.setPointSize(11)
        labelFont.setWeight(65)

        # multijob label
        self.multiJobLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.multiJobLabel.setFont(labelFont)
        self.multiJobLabel.setText("MultiJob")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobLabel)

        # 4 row
        self.multiJobSshPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.multiJobSshPresetLabel.setText(self.SSH_PRESET_LABEL)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobSshPresetLabel)
        self.multiJobSshPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.validator.add('mj_ssh_preset', self.multiJobSshPresetComboBox)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole,
                                  self.multiJobSshPresetComboBox)

        # 5 row
        self.multiJobPbsPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.multiJobPbsPresetLabel.setText(self.PBS_PRESET_LABEL)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole,
                                  self.multiJobPbsPresetLabel)
        self.multiJobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.validator.add('mj_pbs_preset', self.multiJobPbsPresetComboBox)
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole,
                                  self.multiJobPbsPresetComboBox)

        # separator
        sep = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        sep.setText("")
        self.formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, sep)

        # job label
        self.jobLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.jobLabel.setFont(labelFont)
        self.jobLabel.setText("Job")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole,
                                  self.jobLabel)

        # 8 row
        self.jobSshPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.jobSshPresetLabel.setText(self.SSH_PRESET_LABEL)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole,
                                  self.jobSshPresetLabel)
        self.jobSshPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.validator.add('j_ssh_preset', self.jobSshPresetComboBox)
        self.formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole,
                                  self.jobSshPresetComboBox)

        # 9 row
        self.jobPbsPresetLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.jobPbsPresetLabel.setText(self.PBS_PRESET_LABEL)
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole,
                                  self.jobPbsPresetLabel)
        self.jobPbsPresetComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.validator.add('j_pbs_preset', self.jobPbsPresetComboBox)
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole,
                                  self.jobPbsPresetComboBox)

        # separator
        sep = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        sep.setText("")
        self.formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, sep)

        # 11 row
        self.nameLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.nameLabel.setObjectName("nameLabel")
        self.nameLabel.setText("Name:")
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.LabelRole,
                                  self.nameLabel)
        self.nameLineEdit = QtWidgets.QLineEdit(self.mainVerticalLayoutWidget)
        self.nameLineEdit.setObjectName("nameLineEdit")
        self.nameLineEdit.setPlaceholderText("Only alphanumeric characters "
                                             "and - or _")
        self.nameLineEdit.setProperty("clearButtonEnabled", True)
        self.validator.add('name',self.nameLineEdit)
        self.formLayout.setWidget(11, QtWidgets.QFormLayout.FieldRole,
                                  self.nameLineEdit)

        # 12 row
        self.logLevelLabel = QtWidgets.QLabel(self.mainVerticalLayoutWidget)
        self.logLevelLabel.setObjectName("logLevelLabel")
        self.logLevelLabel.setText("Log Level:")
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.LabelRole,
                                  self.logLevelLabel)
        self.logLevelComboBox = QtWidgets.QComboBox(
            self.mainVerticalLayoutWidget)
        self.logLevelComboBox.setObjectName("logLevelComboBox")
        self.logLevelComboBox.addItem(logging.getLevelName(logging.INFO),
                                      logging.INFO)
        self.logLevelComboBox.addItem(logging.getLevelName(logging.WARNING),
                                      logging.WARNING)
        self.logLevelComboBox.setCurrentIndex(0)
        self.formLayout.setWidget(12, QtWidgets.QFormLayout.FieldRole,
                                  self.logLevelComboBox)


        self.horizontalLayout = QtWidgets.QHBoxLayout(dialog)
        self.horizontalLayout.addWidget(self.mainVerticalLayoutWidget)

        self.pbsVerticalLayoutWidget = QtWidgets.QWidget(dialog)
        self.horizontalLayout.addWidget(self.pbsVerticalLayoutWidget)
        dialog.setLayout(self.horizontalLayout)


        # PBS options
        #############

        self.pbs_validator = PbsPresetsValidationColorizer()

        # form layout
        self.pbs_formLayout = QtWidgets.QFormLayout()
        self.pbs_formLayout.setContentsMargins(10, 15, 10, 15)
        self.pbsVerticalLayoutWidget.setLayout(self.pbs_formLayout)

        # form layout
        # separator
        sep = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        sep.setText("")
        sep.setMinimumHeight(40)
        self.pbs_formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, sep)

        # PBS options label
        label = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        label.setFont(labelFont)
        label.setText("PBS options")
        self.pbs_formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, label)

        # 2 row
        self.pbs_nameLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_nameLabel.setText("Name:")
        self.pbs_formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.pbs_nameLabel)
        self.pbs_nameComboBox = PbsComboBox(self.pbsVerticalLayoutWidget)
        self.pbs_nameComboBox.setCompleter(None)
        self.pbs_validator.add('name', self.pbs_nameComboBox)
        self.pbs_AddButton = QtWidgets.QPushButton(self.pbsVerticalLayoutWidget)
        self.pbs_AddButton.setIcon(icon.get_app_icon("add"))
        self.pbs_AddButton.setToolTip('Create new PBS preset')
        self.pbs_AddButton.setMaximumWidth(45)
        self.pbs_RemoveButton = QtWidgets.QPushButton(self.pbsVerticalLayoutWidget)
        self.pbs_RemoveButton.setIcon(icon.get_app_icon("remove"))
        self.pbs_RemoveButton.setToolTip('Remove PBS preset')
        self.pbs_RemoveButton.setMaximumWidth(45)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.pbs_nameComboBox)
        layout.addWidget(self.pbs_AddButton)
        layout.addWidget(self.pbs_RemoveButton)
        self.pbs_formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, layout)

        # 3 row
        self.pbs_pbsSystemLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_pbsSystemLabel.setText("PBS System:")
        self.pbs_formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.pbs_pbsSystemLabel)
        self.pbs_pbsSystemComboBox = QtWidgets.QComboBox(self.pbsVerticalLayoutWidget)
        self.pbs_validator.add('pbs_system', self.pbs_pbsSystemComboBox)
        self.pbs_formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.pbs_pbsSystemComboBox)

        # 4 row
        self.pbs_queueLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_queueLabel.setText("Queue:")
        self.pbs_formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.pbs_queueLabel)
        self.pbs_queueLineEdit = QtWidgets.QLineEdit(self.pbsVerticalLayoutWidget)
        self.pbs_queueLineEdit.setProperty("clearButtonEnabled", True)
        self.pbs_validator.add('queue', self.pbs_queueLineEdit)
        self.pbs_formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.pbs_queueLineEdit)

        # 5 row
        self.pbs_walltimeLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_walltimeLabel.setText("Walltime:")
        self.pbs_formLayout.setWidget(6, QtWidgets.QFormLayout.LabelRole, self.pbs_walltimeLabel)
        self.pbs_walltimeLineEdit = QtWidgets.QLineEdit(self.pbsVerticalLayoutWidget)
        self.pbs_walltimeLineEdit.setPlaceholderText("number of hours")
        self.pbs_walltimeLineEdit.setProperty("clearButtonEnabled", True)
        self.pbs_validator.add('walltime', self.pbs_walltimeLineEdit)
        self.pbs_formLayout.setWidget(6, QtWidgets.QFormLayout.FieldRole, self.pbs_walltimeLineEdit)

        # 6 row
        self.pbs_nodesLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_nodesLabel.setText("Number of Nodes:")
        self.pbs_formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.pbs_nodesLabel)
        self.pbs_nodesSpinBox = QtWidgets.QSpinBox(self.pbsVerticalLayoutWidget)
        self.pbs_nodesSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.pbs_nodesSpinBox.setMinimum(1)
        self.pbs_nodesSpinBox.setMaximum(1000)
        self.pbs_nodesSpinBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.pbs_validator.add('nodes', self.pbs_nodesSpinBox)
        self.pbs_formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.pbs_nodesSpinBox)

        # 7 row
        self.pbs_ppnLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_ppnLabel.setText("Processes per Node:")
        self.pbs_formLayout.setWidget(8, QtWidgets.QFormLayout.LabelRole, self.pbs_ppnLabel)
        self.pbs_ppnSpinBox = QtWidgets.QSpinBox(self.pbsVerticalLayoutWidget)
        self.pbs_ppnSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.pbs_ppnSpinBox.setMinimum(1)
        self.pbs_ppnSpinBox.setMaximum(100)
        self.pbs_ppnSpinBox.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.pbs_validator.add('ppn', self.pbs_ppnSpinBox)
        self.pbs_formLayout.setWidget(8, QtWidgets.QFormLayout.FieldRole, self.pbs_ppnSpinBox)

        # 8 row
        self.pbs_memoryLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_memoryLabel.setText("Memory:")
        self.pbs_formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.pbs_memoryLabel)
        self.pbs_memoryLineEdit = QtWidgets.QLineEdit(self.pbsVerticalLayoutWidget)
        self.pbs_memoryLineEdit.setPlaceholderText("300mb or 1gb")
        self.pbs_memoryLineEdit.setProperty("clearButtonEnabled", True)
        self.pbs_validator.add('memory', self.pbs_memoryLineEdit)
        self.pbs_formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.pbs_memoryLineEdit)

        # 9 row
        self.pbs_infinibandLabel = QtWidgets.QLabel(self.pbsVerticalLayoutWidget)
        self.pbs_infinibandLabel.setText("Infiniband:")
        self.pbs_formLayout.setWidget(10, QtWidgets.QFormLayout.LabelRole, self.pbs_infinibandLabel)
        self.pbs_infinibandCheckBox = QtWidgets.QCheckBox(self.pbsVerticalLayoutWidget)
        self.pbs_validator.add('infiniband', self.pbs_infinibandCheckBox)
        self.pbs_formLayout.setWidget(10, QtWidgets.QFormLayout.FieldRole, self.pbs_infinibandCheckBox)

        return dialog
