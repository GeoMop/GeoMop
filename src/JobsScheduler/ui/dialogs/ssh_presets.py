# -*- coding: utf-8 -*-
"""
Presets dialogs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from ui.dialogs.dialogs import UiPresetsDialog, PresetsDialog
from ui.dialogs.ssh_dialog import SshDialog
import uuid


class SshPresets(PresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None, presets=None):
        super(SshPresets, self).__init__(parent)
        self.ui = UiSshPresets()
        self.ui.setup_ui(self)

        self. presets = presets
        self._reload_view(self.presets)
        self.presets_dlg = SshDialog()

        # connect slots
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.presets_changed.connect(self._reload_view)
        self.ui.btnAdd.clicked.connect(self._handle_add_preset_action)
        self.ui.btnEdit.clicked.connect(self._handle_edit_preset_action)
        self.ui.btnCopy.clicked.connect(self._handle_copy_preset_action)
        self.ui.btnDelete.clicked.connect(self._handle_delete_preset_action)
        self.presets_dlg.accepted.connect(self.handle_presets_dialog)

    def _handle_add_preset_action(self):
        self.presets_dlg.set_purpose(SshDialog.PURPOSE_ADD)
        self.presets_dlg.show()

    def _handle_edit_preset_action(self):
        if self.presets:
            self.presets_dlg.set_purpose(SshDialog.PURPOSE_EDIT)
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            self.presets_dlg.set_data(list(self.presets[index]))
            self.presets_dlg.show()

    def _handle_copy_preset_action(self):
        if self.presets:
            self.presets_dlg.set_purpose(SshDialog.PURPOSE_COPY)
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            data = list(self.presets[index])
            data[0] = None
            data[1] = SshDialog.COPY_PREFIX + " " + data[1]
            self.presets_dlg.set_data(data)
            self.presets_dlg.show()

    def _handle_delete_preset_action(self):
        if self.presets:
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            self.presets.pop(index)
            self.presets_changed.emit(self.presets)

    def handle_presets_dialog(self, purpose, data):
        if purpose != SshDialog.PURPOSE_EDIT:
            data[0] = str(uuid.uuid4())
            self.presets.append(data)
        else:
            for i, item in enumerate(self.presets):
                if item[0] == data[0]:
                    self.presets[i] = data
        self.presets_changed.emit(self.presets)


class UiSshPresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("SshPresetsDialog")
        dialog.setWindowTitle("SSH Presets")
