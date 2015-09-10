# -*- coding: utf-8 -*-
"""
Resource preset
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""

from ui.dialogs.dialogs import UiPresetsDialog, AbstractPresetsDialog
from ui.dialogs.resource_dialog import ResourceDialog


class ResourcePresets(AbstractPresetsDialog):
    """
    Dialog executive code with bindings and other functionality.
    """

    def __init__(self, parent=None, presets=None):
        super(ResourcePresets, self).__init__(parent)

        # setup preset specific UI
        self.ui = UiResourcePresets()
        self.ui.setup_ui(self)

        # assign presets and reload view
        self. presets = presets
        self._reload_view(self.presets)

        # set custom dialog
        self.presets_dlg = ResourceDialog()

        # connect generic presets slots (must be called after UI setup)
        super(ResourcePresets, self)._connect_slots()


class UiResourcePresets(UiPresetsDialog):
    """
    UI extensions of presets dialog.
    """
    def setup_ui(self, dialog):
        super().setup_ui(dialog)

        # dialog properties
        dialog.resize(680, 510)
        dialog.setObjectName("ResourcePresetsDialog")
        dialog.setWindowTitle("Resource Presets")
