from gm_base.geometry_files.format_last import InterpolatedNodeSet


class InterpolatedNodeSetItem:
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

    def save(self):
        return InterpolatedNodeSet(dict(surf_nodesets=[self.top_itf_node_set.save(),
                                                       self.bottom_itf_node_set.save()],
                                        interface_id=self.interface.index))