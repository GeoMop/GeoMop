# -*- coding: utf-8 -*-
"""
Resource preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from JobPanel.ui.dialogs.dialogs import UiPresetsDialog, APresetsDialog
from JobPanel.ui.dialogs.resource_dialog import ResourceDialog


class ResourcePresets(APresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent, presets, pbs=None, ssh=None):
        self.ui = UiResourcePresets()
        """Form builed"""
        self.pbs = pbs
        self.ssh = ssh   
        super().__init__(parent, presets, ResourceDialog) 
        self.presets_dlg.set_pbs_presets(self.pbs)
        self.presets_dlg.set_ssh_presets(self.ssh) 
        self.presets_dlg.valid()
 

class UiResourcePresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setWindowTitle("Resources")
