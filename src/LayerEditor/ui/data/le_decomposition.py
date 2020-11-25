from bgem.polygons.polygons import PolygonDecomposition
from bgem.polygons import polygons

from LayerEditor.ui.tools import undo
import gm_base.geometry_files.format_last as gs



class LEDecomposition(PolygonDecomposition):
    def __init__(self, nodes=None, topology=None):
        super(LEDecomposition, self).__init__()
        if nodes is not None and topology is not None:
            self.deserialize(nodes, topology)
        self.block = None

    def new_point(self, pos, last_point):
        """Add continuous line and point, from self.last_point
        - **parameters**
            :pos: pos of new point
            :last_point: point from which the line begins
        """
        with undo.group("Added Point"):
            pt = self.add_point((pos.x(), -pos.y()))
            #self.block.init_regions_for_new_shape(0, pt.id)

            split_shapes_after_point = []

            if last_point is not None:
                split_shapes_after_point = list(self.last_split_shapes)
                for seg in self.add_line_for_points(last_point.pt, pt):
                    self.block.init_regions_for_new_shape(1, seg.id)
                    # for poly_id in self.polygons:
                    #     if poly_id != 0:
                    #         self.block.init_regions_for_new_shape(2, poly_id)

            for dim, id_old, id_new in self.last_split_shapes + split_shapes_after_point:
                # if some shape was split then copy region to the new shape
                if dim == 2 and id_old == 0:
                    continue
                for layer in self.block.layers_dict.values():
                    region = layer.get_shape_region(dim, id_old)
                    layer.set_region_to_shape(dim, id_new, region)

            self.initialize_regions()

            return pt

    def initialize_regions(self):
        """Initializes regions for all shapes which dont have defined regions. If region is defined it is ignored."""
        for dim in range(3):
            for item_id in self.decomp.shapes[dim]:
                self.block.init_regions_for_new_shape(dim, item_id)

    def delete_items(self, items):
        """Delete all points and segments"""
        with undo.group("Delete selected"):
            for dim, id in items:
                if dim == 1:
                    self.delete_segment(self.segments[id])

            for dim, id in items:
                if dim == 0:
                    self.delete_point(self.points[id])

    def copy_itself(self):
        """ Make new decomposition with identical topology and nodeset as this.
            Ids will change, so everything that uses shape ids needs to be updated using old_to_new_id"""
        receiver = undo.stack()._receiver
        nodes, topology = self.serialize()

        old_to_new_id = [{}, {}, {}]
        for dim in range(3):
            for shape in self.decomp.shapes[dim].values():
                old_to_new_id[dim][shape.id] = shape.index

        cpy = LEDecomposition(nodes, topology)

        cpy.block = self.block
        undo.stack().setreceiver(receiver)
        return cpy, old_to_new_id

    # Moved here from polygon_io.py
    def serialize(self):
        """
        Serialization of the PolygonDecomposition, into geometry objects, storing:
        - nodes, given by coordinates (x,y)
        - segments, given by node indices in nodes array: (out_vtx_idx, in_vtx_idx)
        - polygons, given as:
            - list of segments on outer wire
            - list of holes, every hole is list of segments in its wire
            - list of free points inside the polygon
        After call of this function, every node, segment, polygon have attribute 'index'
        containing the index of the object in the output file lists.
        :param polydec: PolygonDecomposition
        :return: (nodes, topology)
        """

        def set_indices():
            """
            Asign index to every node, segment and ppolygon.
            :return: None
            """
            for shapes in self.decomp.shapes:
                for idx, obj in enumerate(shapes.values()):
                    obj.index = idx

        decomp = self.decomp
        decomp.check_consistency()
        set_indices()
        nodes = [list(pt.xy) for pt in decomp.points.values()]
        topology = gs.Topology()

        topology.segments = []
        for seg in decomp.segments.values():
            segment = gs.Segment(dict(node_ids=(seg.vtxs[0].index, seg.vtxs[1].index)))
            topology.segments.append(segment)

        topology.polygons = []
        for poly in decomp.polygons.values():
            polygon = gs.Polygon()
            polygon.segment_ids = [seg.index for seg, side in poly.outer_wire.segments()]
            polygon.holes = []
            for hole in poly.outer_wire.childs:
                wire = [seg.index for seg, side in hole.segments()]
                polygon.holes.append(wire)
            polygon.free_points = [pt.index for pt in poly.free_points]
            topology.polygons.append(polygon)
        return (nodes, topology)

    def deserialize(self, nodes, topology):
        """
        Deserialize PolygonDecomposition, reconstruct all internal information.
        :param nodes: list of node coordinates, (x,y)
        :param topology: Geometry, Topology object, containing: nodes, segments and polygons
        produced by serialize function.
        :return: PolygonDecomposition. The attributes 'id' and 'index' of nodes, segments and polygons
        are set to their indices in the input file lists, counting from 0.
        """
        polygons.disable_undo()
        decomp = self.decomp

        for id, node in enumerate(nodes):
            self._add_point(node, poly=self.outer_polygon)

        if len(topology.polygons) == 0 or len(topology.polygons[0].segment_ids) > 0:
            self.reconstruction_from_old_input(topology)
            return

        for id, seg in enumerate(topology.segments):
            vtxs_ids = seg.node_ids
            s = self.make_segment(vtxs_ids)
            s.index = id
            assert s.id == id

        for id, poly in enumerate(topology.polygons):
            free_pt_ids = poly.free_points
            p = self.make_polygon(poly.segment_ids, poly.holes, free_pt_ids)
            p.index = id
            assert p.id == id

        self.set_wire_parents()

        decomp.check_consistency()
        polygons.enable_undo()
        return

    def reconstruction_from_old_input(self, topology):
        # Set points free
        for pt in self.points.values():
            pt.set_polygon(self.outer_polygon)

        for id, seg in enumerate(topology.segments):
            vtxs = [self.points[pt_id] for pt_id in seg.node_ids]
            s = self.new_segment(vtxs[0], vtxs[1])
            s.index = id
            assert s.id == id

        self.outer_polygon.index = 0
        for id, poly in enumerate(topology.polygons):
            segments = {seg_id for seg_id in poly.segment_ids}
            candidates = []
            for p in self.polygons.values():
                seg_set = set()
                for seg, side in p.outer_wire.segments():
                    seg_set.add(seg.index)
                if segments.issubset(seg_set):
                    candidates.append(p)

            assert len(candidates) == 1
            candidates[0].index = id + 1
        self.decomp.check_consistency()


