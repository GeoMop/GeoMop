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

    def __init__(self, parent, presets):
        self.ui = UiEnvPresets()        
        super().__init__(parent, presets, EnvDialog)


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
