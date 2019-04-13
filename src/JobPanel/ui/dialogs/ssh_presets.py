# -*- coding: utf-8 -*-
"""
Ssh preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from JobPanel.ui.dialogs.dialogs import UiPresetsDialog, APresetsDialog
from JobPanel.ui.dialogs.ssh_dialog import SshDialog


class SshPresets(APresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent, presets, container, frontend_service):
        self.ui = UiSshPresets()
        """Form builed"""
        super().__init__(parent, presets, SshDialog)
        self.presets_dlg.set_data_container(container, frontend_service)


class UiSshPresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(700, 560)
        dialog.setObjectName("SshPresetsDialog")
        dialog.setWindowTitle("SSH hosts")
