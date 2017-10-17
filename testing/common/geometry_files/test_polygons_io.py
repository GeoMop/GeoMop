import geometry_files.polygons_io as polygons_io
import geometry_files.polygons as polygons

def test_polygons_io():
    decomp = polygons.PolygonDecomposition()
    decomp.add_line((0, 0), (3, 0))
    decomp.add_line((0, 0), (0, 3))
    decomp.add_line((0, 3), (3, 0))
    decomp.add_line((1, 1), (2, 1))
    decomp.add_line((1, 1), (1, 2))
    decomp.add_line((1, 2), (2, 1))

    nodes, topology = polygons_io.serialize(decomp)

    nodes_id_map = { id: (id, node) for id, node in enumerate(nodes) }
    new_decomp = polygons_io.deserialize(nodes_id_map, topology)
    print(decomp)
    print(new_decomp)