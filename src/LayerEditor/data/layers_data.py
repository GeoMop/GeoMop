"""
Data structures for the Layers application.

GUI is used to manipulate these data structures.
Data structures are close to the input/output JSON fromat described by classes in
gm_base.geometry_files.format_last
"""

from gm_base.geometry_files import format_last as IO


class Region(IO.Region):
    def __init__(self, region):
        pass

class Surface(IO.Surface):
    def __init__(selfself, surface):

        self._interfaces = set()
        # Connected interfaces

class Interface(IO.Interface):
    def __init__(self, interface):
        pass

    """
    Invetible operations.
    """
    def set_surface(self, new_surface, new_transform):
        return (self.set_surface, old surface, old transform)



class StratumLayer(IO.StratumLayer):
    def __init__(self, layer, lg):
        pass

class FractureLayer(IO.FractureLayer):
    def __init__(self, layer, lg):
        pass

    def connect_interface(self, side, interface):
        return (self.disconnect_interface, side)

    def disconnect_interface(self, side):
        return (self.connect_interface, side, interface)




class Block:
    def __init__(self, layers):
        self._layers = layers

    def decompositions(self):
        """
        Generator iterating over all decompositions of the block.
        """
        last_decomp = None
        for layer in self._layers:
            decomp = layer.top_decomp
            if decomp is not last_decomp:
                last_decomp = decomp
                yield decomp
            decomp = layer.bot_decomp
            if decomp is not last_decomp:
                last_decomp = decomp
                yield decomp


class LayersGeometry:
    @classmethod
    def default_file(cls):
        """
        Consturuction of a new file with single layer with default name and depth.
        TODO: use zero state of LayersGeometry and add the layer using natural data operations.
        :return: default IO.LayerGeometry
        """
        lg = IO.LayerGeometry()

        # TODO: version should be set in the IO.LayerGeometry constructor
        lg.version = [0, 5, 5]

        default_regions =
        lg.regions = [
            IO.Region(dict(color="##", name="NONE", not_used=True, dim=IO.RegionDim.none))
        ]

        # Single empty layer
        regions = ([], [], [])  # No node, segment, polygon or regions.
        top_interface = Interface(dict(elevation=0.0, surface_id=None))
        top_interface.transform_z = [1.0, 0.0]
        bot_interface = Interface(dict(elevation=-100.0, surface_id=None))
        bot_interface.transform_z = [1.0, 0.0]
        lg.interfaces = [top_interface, bot_interface]
        i_top_iface, i_bot_iface = [0, 1]

        top_ns = IO.InterfaceNodeSet(dict(
            nodeset_id=0, interface_id=i_top_iface ))

        surf_nodesets = (dict(nodeset_id=0, interface_id=i_bot_iface),
                         dict(nodeset_id=0, interface_id=i_bot_iface))
        bot_ns = IO.InterpolatedNodeSet(dict(
            surf_nodesets=surf_nodesets, interface_id=i_bot_iface) )

        lname = "Layer_1"
        gl = IO.StratumLayer(dict(name=lname, top=top_ns, bottom=bot_ns))
        lg.layers.append(gl)
        lg.topologies.append(IO.Topology())
        tp_idx = 0
        lg.node_sets.append( NodeSet(dict(topology_id=tp_idx, nodes=[])) )
        ns_idx = 0
        lg.node_sets.append(ns)
        lg.supplement.last_node_set = ns_idx
        return lg

    def __init__(self, lg):
        """

        """
        self._regions = {}
        # Map region id to Region (simple descendent of IO.Region)
        self._layers = []
        # Stratum and fracture layers from top to bottom
        self._interfaces = {}
        #
        self._surfaces = {}
        #
        self._decompositions = {}
        # InterfaceNodeset and InterpolatedNodeset combine topology and nodeset into
        # decomposition. Layeers are bounderd by decompositions instead of nodesets.
        # Map (topology_index,  nodeset_index) to decomposition objects
        self._blocks = []
        # Blocks are lists of layers with same topology, we must maintain same topology for
        # decompositions in te same block

        self.load(self.default_file())

    def fill_new_data(self):
        """
        Fill new file content to the empty LayerGeometry.
        :return:
        """
        self.add_layer(name=)
        return self

    def load(self, io_layer_geometry):
        """
        Load from file format main class.
        :param io_layer_geometry: instance of IO.LayerGeometry
        :return: None
        """


    def save(self):
        """
        Save to main file format class.
        :return: instance of IO.LayerGeometry
        """

    """
    Invetible operations.
    """

    def connect_layer_to (self):
        pass
    def merge_layers(self):
        pass


    def insert_layer


