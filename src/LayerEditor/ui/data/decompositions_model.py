from LayerEditor.ui.data.le_decomposition import LEDecomposition
from LayerEditor.ui.tools import undo
from gm_base.geometry_files.format_last import NodeSet


class DecompositionsModel:
    """Each nodeset defines one decomposition. This class"""
    def __init__(self, node_sets_data: list, topologies_data: list):
        self.decomps = []
        for node_set in node_sets_data:
            self.decomps.append(LEDecomposition(node_set.nodes,
                                                topologies_data[node_set.topology_id]))

    def save(self):
        node_sets = []
        topologies = []
        helper_blocks = []
        for idx, decomp in enumerate(self.decomps):
            nodes, topology = decomp.serialize()
            decomp.temp_index = idx
            if decomp.block in helper_blocks:
                top_id = topologies.index(topology)
            else:
                topologies.append(topology)
                helper_blocks.append(decomp.block)
                top_id = len(topologies) - 1
            node_sets.append(NodeSet(dict(topology_id=top_id, nodes=nodes)))
        return node_sets, topologies

    def clear_indexing(self):
        for decomp in self.decomps:
            del decomp.temp_index

    @undo.undoable
    def add_decomposition(self, decomp):
        self.decomps.append(decomp)
        yield "Add Decomposition"
        self.decomps.remove(decomp)

    @undo.undoable
    def delete_decomposition(self, decomp):
        idx = self.decomps.index(decomp)
        self.decomps.remove(decomp)
        yield "Delete Decomposition"
        self.decomps.insert(idx, decomp)


