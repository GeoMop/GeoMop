# -*- coding: utf-8 -*-
"""
Pbs preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from ui.dialogs.dialogs import UiPresetsDialog, APresetsDialog
from ui.dialogs.env_dialog import EnvDialog


class EnvPresets(APresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None, presets=None):
        super().__init__(parent)

        # setup preset specific UI
        self.ui = UiEnvPresets()
        self.ui.setup_ui(self)

        # assign presets and reload view
        self.presets = presets
        self.reload_view(self.presets)

        self.DlgClass = EnvDialog

        # connect generic presets slots (must be called after UI setup)
        super().connect_slots()


class UiEnvPresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """

    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("EnvPresetsDialog")
        dialog.setWindowTitle("Environments")
