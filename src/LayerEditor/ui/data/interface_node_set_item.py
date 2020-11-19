from LayerEditor.ui.tools import undo
from gm_base.geometry_files.format_last import InterfaceNodeSet


class InterfaceNodeSetItem:
    is_interpolated = False
    def __init__(self, decomp, interface):
        self.decomposition = decomp
        """Node set index"""
        self.interface = interface
        """Interface index"""

    def get_shapes(self):
        """Topology must be the same so shape should be too"""
        return self.decomposition.decomp.shapes

    @property
    def block(self):
        return self.decomposition.block

    def save(self):
        return InterfaceNodeSet(dict(nodeset_id=self.decomposition.temp_index,
                                     interface_id=self.interface.index))

    def __eq__(self, other):
        if (self.interface == other.interface and
                isinstance(other, InterfaceNodeSetItem) and
                self.decomposition == other.decomposition):
            return True
        return False

    @undo.undoable
    def change_decomposition(self, top_decomp, bot_decomp=None):
        """bot_decomp is present only so this method is identical to the one in InterpolatedNodeSetItem"""
        old_decomp = self.decomposition
        self.decomposition = top_decomp
        yield "Changing Decomposition"
        self.decomposition = old_decomp


