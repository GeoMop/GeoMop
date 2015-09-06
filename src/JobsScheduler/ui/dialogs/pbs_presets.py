# -*- coding: utf-8 -*-
"""
Presets dialogs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets, QtCore

from ui.dialogs.dialogs import UiPresetsDialog
from ui.dialogs.pbs_dialog import PbsDialog
import uuid


class PbsPresets(QtWidgets.QDialog):
    """
    Dialog executive code with bindings and other functionality.
    """
    presets = None
    presets_changed = QtCore.pyqtSignal(list)

    def __init__(self, parent=None, presets=None):
        super(PbsPresets, self).__init__(parent)
        self.ui = UiPbsPresets()
        self.ui.setup_ui(self)

        self. presets = presets
        self.presets_dlg = PbsDialog()

        # connect slots
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

        self.presets_changed.connect(self._reload_view)
        self.ui.btnAdd.clicked.connect(self._handle_add_preset_action)
        self.ui.btnEdit.clicked.connect(self._handle_edit_preset_action)
        self.ui.btnCopy.clicked.connect(self._handle_copy_preset_action)
        self.ui.btnDelete.clicked.connect(self._handle_delete_preset_action)
        self.presets_dlg.accepted.connect(self.handle_presets_dialog)

    def _reload_view(self, presets):
        self.ui.presets.clear()
        if presets:
            for row_id, row in enumerate(presets):
                QtWidgets.QTreeWidgetItem(self.ui.presets)
                for col_id, item in enumerate(row[1:]):
                    self.ui.presets.topLevelItem(row_id).setText(col_id,
                                                                 str(item))

    def _handle_add_preset_action(self):
        self.presets_dlg.set_purpose(PbsDialog.PURPOSE_ADD)
        self.presets_dlg.show()

    def _handle_edit_preset_action(self):
        if self.presets:
            self.presets_dlg.set_purpose(PbsDialog.PURPOSE_EDIT)
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            self.presets_dlg.set_data(list(self.presets[index]))
            self.presets_dlg.show()

    def _handle_copy_preset_action(self):
        if self.presets:
            self.presets_dlg.set_purpose(PbsDialog.PURPOSE_COPY)
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            data = list(self.presets[index])
            data[0] = None
            data[1] = "Copy of " + data[1]
            self.presets_dlg.set_data(data)
            self.presets_dlg.show()

    def _handle_delete_preset_action(self):
        if self.presets:
            index = self.ui.presets.indexOfTopLevelItem(
                self.ui.presets.currentItem())
            self.presets.pop(index)
            self.presets_changed.emit(self.presets)

    def handle_presets_dialog(self, purpose, data):
        if purpose != PbsDialog.PURPOSE_EDIT:
            data[0] = str(uuid.uuid4())
            self.presets.append(data)
        else:
            for i, item in enumerate(self.presets):
                if item[0] == data[0]:
                    self.presets[i] = data
        self.presets_changed.emit(self.presets)


class UiPbsPresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("PbsPresetsDialog")
        dialog.setWindowTitle("PBS Presets")
