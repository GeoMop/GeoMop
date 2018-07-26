# -*- coding: utf-8 -*-
"""
Pbs preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from JobPanel.ui.dialogs.dialogs import UiPresetsDialog, APresetsDialog
from JobPanel.ui.dialogs.pbs_dialog import PbsDialog


class PbsPresets(APresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent, presets):
        self.ui = UiPbsPresets()
        """Form builed"""
        super().__init__(parent, presets, PbsDialog)

class UiPbsPresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("PbsPresetsDialog")
        dialog.setWindowTitle("PBS options")
