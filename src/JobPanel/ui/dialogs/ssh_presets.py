# -*- coding: utf-8 -*-
"""
Ssh preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from ui.dialogs.dialogs import UiPresetsDialog, APresetsDialog
from ui.dialogs.ssh_dialog import SshDialog


class SshPresets(APresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None, presets=None, container=None):
        super().__init__(parent)

        # setup preset specific UI
        self.ui = UiSshPresets()
        self.ui.setup_ui(self)

        # assign presets and reload view
        self.set_presets(presets)

        self.DlgClass = SshDialog
        self.container = container

        # connect generic presets slots (must be called after UI setup)
        super().connect_slots()
        
    def create_dialog(self):
        super(SshPresets, self).create_dialog()
        self.presets_dlg.set_data_container(self.container)
        

class UiSshPresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("SshPresetsDialog")
        dialog.setWindowTitle("SSH hosts")
