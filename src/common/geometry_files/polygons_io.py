import os
import sys

geomop_src = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.append(geomop_src)

import geometry_files.geometry_structures as gs
import geometry_files.polygons as polygons

def serialize(decomp):
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


def deserialize(input_id_to_node, topology):
    decomp = polygons.PolygonDecomposition()

    for id, node in input_id_to_node.values():
        decomp.points.append(polygons.Point(node, poly=None), id=id)

    for seg in topology.segments:
        vtxs_ids = [input_id_to_node[id][0] for id in seg.node_ids]
        decomp.make_segment(vtxs_ids)

    for poly in topology.polygons:
        free_pt_ids = [input_id_to_node[id][0] for id in poly.free_points]
        decomp.make_polygon(poly.segment_ids, poly.holes, free_pt_ids)

    print(decomp)
    decomp.set_wire_parents()
    decomp.check_consistency()

    return decomp
