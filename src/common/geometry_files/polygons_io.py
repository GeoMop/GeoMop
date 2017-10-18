import os
import sys

geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

import geometry_files.geometry_structures as gs
import geometry_files.polygons as polygons

def serialize(decomp):
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
    :param decomp: PolygonDecomposition
    :return: (nodes, topology)
    """
    decomp.check_consistency()
    decomp.make_indices()
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
    :return: PolygonDecomposition. The attributes 'id' and 'index' of nodes, segments and polygons
    are set to their indices in the input file lists, counting from 0.
    """
    decomp = polygons.PolygonDecomposition()

    for id, node in enumerate(nodes):
        node = decomp.points.append(polygons.Point(node, poly=None), id=id)
        node.index = id

    for id, seg in enumerate(topology.segments):
        vtxs_ids = seg.node_ids
        s = decomp.make_segment(vtxs_ids)
        s.index = id
        assert s.id == id

    for id, poly in enumerate(topology.polygons):
        free_pt_ids = poly.free_points
        p = decomp.make_polygon(poly.segment_ids, poly.holes, free_pt_ids)
        p.index = id
        assert p.id == id

    #print(decomp)
    decomp.set_wire_parents()
    decomp.check_consistency()

    return decomp
