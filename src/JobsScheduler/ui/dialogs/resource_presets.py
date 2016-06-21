# -*- coding: utf-8 -*-
"""
Resource preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from ui.dialogs.dialogs import UiPresetsDialog, APresetsDialog
from ui.dialogs.resource_dialog import ResourceDialog


class ResourcePresets(APresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None, presets=None, pbs=None, ssh=None,
                 env=None):
        super().__init__(parent)

        # setup preset specific UI
        self.ui = UiResourcePresets()
        self.ui.setup_ui(self)

        # assign presets and reload view
        self. presets = presets
        self.reload_view(self.presets)

        self.pbs = pbs
        self.ssh = ssh
        self.env = env
        self.DlgClass = ResourceDialog

        # connect generic presets slots (must be called after UI setup)
        super().connect_slots()

    def create_dialog(self):
        super(ResourcePresets, self).create_dialog()
        self.presets_dlg.set_pbs_presets(self.pbs)
        self.presets_dlg.set_ssh_presets(self.ssh)
        self.presets_dlg.set_env_presets(self.env)


class UiResourcePresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("ResourcePresetsDialog")
        dialog.setWindowTitle("Resources")
