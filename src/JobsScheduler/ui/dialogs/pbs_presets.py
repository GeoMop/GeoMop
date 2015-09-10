# -*- coding: utf-8 -*-
"""
Pbs preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from ui.dialogs.dialogs import UiPresetsDialog, AbstractPresetsDialog
from ui.dialogs.pbs_dialog import PbsDialog


class PbsPresets(AbstractPresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None, presets=None):
        super(PbsPresets, self).__init__(parent)

        # setup preset specific UI
        self.ui = UiPbsPresets()
        self.ui.setup_ui(self)

        # assign presets and reload view
        self. presets = presets
        self._reload_view(self.presets)

        # set custom dialog
        self.presets_dlg = PbsDialog()

        # connect generic presets slots (must be called after UI setup)
        super(PbsPresets, self)._connect_slots()


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
