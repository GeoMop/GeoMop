from geometry_files.geometry_factory import  GeometryFactory
from geometry_files.geometry import GeometrySer
import shutil
import os

TEST_DIR = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "test_geometry")

def test_local(request):
    if not os.path.isdir(TEST_DIR):
        os.makedirs(TEST_DIR)
    def fin_remove_test_dir():        
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    request.addfinalizer(fin_remove_test_dir)

    
    points1 = [[100, 100], [200, 200], [300, 100], [100, 200]]
    points2 = [[101, 101], [201, 500], [301, 101], [101, 201]]
    lines1 = [[0, 1], [1, 2], [2, 3], [3, 0]]
    lines2 = [[0, 2], [2, 1], [1, 3], [3, 0]]
    gf = GeometryFactory()
    tp1_idx = gf.add_topology()
    tp2_idx = gf.add_topology()
    ns11_idx = gf.add_node_set(tp1_idx)
    ns12_idx = gf.add_node_set(tp1_idx)
    ns21_idx = gf.add_node_set(tp2_idx)
    ns22_idx = gf.add_node_set(tp2_idx)
    for point in points1:
        gf.add_point(ns11_idx, point[0], point[1])
        gf.add_point(ns12_idx, point[0], point[1])
    for point in points2:
        gf.add_point(ns21_idx, point[0], point[1])
        gf.add_point(ns22_idx, point[0], point[1])
    for line in lines1:
        gf.add_segment( tp1_idx, line[0], line[1])
    for line in lines2:
        gf.add_segment( tp2_idx, line[0], line[1])
    assert  tp1_idx==0 and tp2_idx==1
    assert  ns11_idx==0 and ns12_idx==1 and ns21_idx==2 and ns22_idx==3
    assert gf.geometry.node_sets[0].topology_idx== tp1_idx
    assert gf.geometry.node_sets[1].topology_idx== tp1_idx
    assert gf.geometry.node_sets[2].topology_idx== tp2_idx
    assert gf.geometry.node_sets[3].topology_idx== tp2_idx
    
    reader = GeometrySer(os.path.join(TEST_DIR, "test_geometry1.json"))
    reader.write(gf.geometry)
    new_geometry =  reader.read()

    assert new_geometry.node_sets[0].topology_idx== tp1_idx
    assert new_geometry.node_sets[1].topology_idx== tp1_idx
    assert new_geometry.node_sets[2].topology_idx== tp2_idx
    assert new_geometry.node_sets[3].topology_idx== tp2_idx
    
    
    
    
    
