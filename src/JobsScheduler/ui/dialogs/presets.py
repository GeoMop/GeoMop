# -*- coding: utf-8 -*-
"""
Presets dialogs
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from PyQt5 import QtWidgets

from ui.dialogs.dialogs import UiPresetsDialog


class SshPresets(QtWidgets.QDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None):
        super(SshPresets, self).__init__(parent)
        self.ui = UiSshPresets()
        self.ui.setup_ui(self)

        self._connect_slots_()
        self.show()

    def _connect_slots_(self):
        # QtCore.QMetaObject.connectSlotsByName(self)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)


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

        item_0 = QtWidgets.QTreeWidgetItem(self.presets)
        self.presets.topLevelItem(0).setText(0, "tarkill")
        self.presets.topLevelItem(0).setText(1, "FrontEnd at MetaCentrum")

        item_1 = QtWidgets.QTreeWidgetItem(self.presets)
        self.presets.topLevelItem(1).setText(0, "ostrava")
        self.presets.topLevelItem(1).setText(1, "SuperComputer in Ostrava")

