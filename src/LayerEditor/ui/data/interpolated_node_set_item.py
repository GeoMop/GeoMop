from LayerEditor.ui.tools import undo
from gm_base.geometry_files.format_last import InterpolatedNodeSet


class InterpolatedNodeSetItem:
    is_interpolated = True
    def __init__(self, itf_node_set1, itf_node_set2, interface):
        if itf_node_set1.interface.elevation > itf_node_set2.interface.elevation:
            self.top_itf_node_set = itf_node_set1
            self.bottom_itf_node_set = itf_node_set2
        else:
            self.top_itf_node_set = itf_node_set2
            self.bottom_itf_node_set = itf_node_set1
        """Top and bottom node set index"""
        self.interface = interface
        """Interface index"""

    def is_top_and_bottom_equal(self):
        return self.top_itf_node_set == self.bottom_itf_node_set

    def get_shapes(self):
        """Topology must be the same so shape should be too"""
        return self.top_itf_node_set.decomposition.decomp.shapes

    @property
    def block(self):
        return self.top_itf_node_set.decomposition.block

    def save(self):
        return InterpolatedNodeSet(dict(surf_nodesets=(self.top_itf_node_set.save(),
                                                       self.bottom_itf_node_set.save()),
                                        interface_id=self.interface.index))

    @undo.undoable
    def change_decomposition(self, top_decomp, bot_decomp):
        self.top_itf_node_set.change_decomposition(top_decomp)
        self.bottom_itf_node_set.change_decomposition(bot_decomp)

    def __eq__(self, other):
        if     (self.interface == other.interface and
                isinstance(other, InterpolatedNodeSetItem) and
                self.top_itf_node_set == other.top_itf_node_set and
                self.bottom_itf_node_set == other.bottom_itf_node_set):
            return True
        return False
