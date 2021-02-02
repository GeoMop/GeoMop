from LayerEditor.ui.tools import undo


class INodeSetItem:
    def __init__(self, interface):
        self.interface = interface
        """InterfaceItem defining surface (elevation)"""

    @property
    def decomposition(self):
        assert False, "Abstract function! Must be overridden by child class!"

    @property
    def block(self):
        return self.decomposition.block

    @undo.undoable
    def change_decomposition(self, top_decomp, bot_decomp):
        assert False, "Abstract function! Must be overridden by child class!"



