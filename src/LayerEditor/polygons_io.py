import gm_base.geometry_files.format_last as gs
import bgem.polygons.polygons as polygons

"""
TODO: Try to remove dependency on `decomp` module.
"""
# TODO: ^ seems to be done.
# TODO: Maybe put those methods somewhere close to decomposition (for example DiagramScene)


def set_indices(decomp):
    """
    Asign index to every node, segment and ppolygon.
    :return: None
    """
    for shapes in decomp.shapes:
        for idx, obj in enumerate(shapes.values()):
            obj.index = idx


def serialize(polydec):
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
    decomp = polydec.decomp
    decomp.check_consistency()
    set_indices(decomp)
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


def deserialize(nodes, topology):
    """
    Deserialize PolygonDecomposition, reconstruct all internal information.
    :param nodes: list of node coordinates, (x,y)
    :param topology: Geometry, Topology object, containing: nodes, segments and polygons
    produced by serialize function.
    :return: PolygonDecomposition. The attribute 'id' of nodes, segments and polygons
    are set to their indices in the input file lists, counting from 0.
    """
    polydec = polygons.PolygonDecomposition()
    polygons.disable_undo()
    decomp = polydec.decomp

    for id, node in enumerate(nodes):
        point = polydec._add_point(node, poly=polydec.outer_polygon)
        assert point.id == id

    if len(topology.polygons) == 0 or len(topology.polygons[0].segment_ids) > 0:
        reconstruction_from_old_input(polydec, topology)
        return polydec

    for id, seg in enumerate(topology.segments):
        vtxs_ids = seg.node_ids
        s = polydec.make_segment(vtxs_ids)
        assert s.id == id

    for id, poly in enumerate(topology.polygons):
        free_pt_ids = poly.free_points
        p = polydec.make_polygon(poly.segment_ids, poly.holes, free_pt_ids)
        assert p.id == id

    polydec.set_wire_parents()

    decomp.check_consistency()
    polygons.enable_undo()
    return polydec


def reconstruction_from_old_input(polydec, topology):
    # Set points free
    for pt in polydec.points.values():
        pt.set_polygon(polydec.outer_polygon)

    for id, seg in enumerate(topology.segments):
        vtxs = [polydec.points[pt_id] for pt_id in seg.node_ids]
        s = polydec.new_segment(vtxs[0], vtxs[1])
        assert s.id == id

    for id, poly in enumerate(topology.polygons):
        segments = {seg_id for seg_id in poly.segment_ids}
        candidates = []
        for p in polydec.polygons.values():
            seg_set = set()
            for seg, side in p.outer_wire.segments():
                seg_set.add(seg.id)
            if segments.issubset(seg_set):
                candidates.append(p)

        assert len(candidates) == 1
    polydec.decomp.check_consistency()

