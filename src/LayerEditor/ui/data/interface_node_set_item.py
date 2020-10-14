from gm_base.geometry_files.format_last import InterfaceNodeSet


class InterfaceNodeSetItem:
    def __init__(self, decomp, interface):
        self.decomposition = decomp
        """Node set index"""
        self.interface = interface
        """Interface index"""

    def save(self):
        return InterfaceNodeSet(dict(nodeset_id=self.decomposition.temp_index,
                                     interface_id=self.interface.index))