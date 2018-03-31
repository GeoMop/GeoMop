import gm_base.polygons.polygons_io as polygons_io
import gm_base.polygons.polygons as polygons

def test_set_indices():
    decomp = polygons.PolygonDecomposition()
    sg0, = decomp.add_line((0, 0), (0, 2))
    decomp.add_line((0, 0), (2, 0))
    sg2, = decomp.add_line((0, 2), (2, 0))
    polygons_io.set_indices(decomp.decomp)
    assert sg2.index == 2
    assert decomp.decomp.polygons[0].index == 0
    assert decomp.decomp.polygons[1].index == 1


def test_polygons_io():
    decomp = polygons.PolygonDecomposition()
    seg0, = decomp.add_line((0, 0), (3, 0))
    decomp.add_line((0, 0), (0, 3))
    decomp.add_line((0, 3), (3, 0))
    decomp.add_line((1, 1), (2, 1))
    decomp.add_line((1, 1), (1, 2))
    seg5, = decomp.add_line((1, 2), (2, 1))
    assert seg0.id == 0
    assert seg5.id == 5

    nodes, topology = polygons_io.serialize(decomp)

    nodes_id_map = { id: (id, node) for id, node in enumerate(nodes) }
    new_decomp = polygons_io.deserialize(nodes_id_map, topology)
    print(decomp)
    print(new_decomp)