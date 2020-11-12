from gm_base.geometry_files.format_last import InterfaceNodeSet


class InterfaceNodeSetItem:
    is_interpolated = False
    def __init__(self, decomp, interface):
        self.decomposition = decomp
        """Node set index"""
        self.interface = interface
        """Interface index"""

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