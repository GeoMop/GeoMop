from LayerEditor.ui.data.abstract_model import AbstractModel
from LayerEditor.ui.data.le_decomposition import LEDecomposition
from LayerEditor.ui.tools import undo
from LayerEditor.ui.tools.id_map import IdObject
from gm_base.geometry_files.format_last import NodeSet


class DecompositionsModel(AbstractModel):
    """Each nodeset defines one decomposition. This class manages all the decompositions."""

    def deserialize(self, node_sets_data, topologies_data, blocks_model):
        """ Initializes decompositions model with data from format_last.py"""
        for node_set in node_sets_data:
            decomp = LEDecomposition.create_from_data(node_set.nodes,
                                                      topologies_data[node_set.topology_id],
                                                      blocks_model[node_set.topology_id])
            with undo.pause_undo():
                self.add(decomp)

    def serialize(self):
        node_sets = []
        topologies = []
        helper_blocks = []
        for idx, decomp in enumerate(self.items()):
            nodes, topology = decomp.serialize()
            decomp.index = idx
            if decomp.block in helper_blocks:
                top_id = topologies.index(topology)
            else:
                topologies.append(topology)
                helper_blocks.append(decomp.block)
                top_id = len(topologies) - 1
            node_sets.append(NodeSet(dict(topology_id=top_id, nodes=nodes)))
        return node_sets, topologies




