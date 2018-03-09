import testing.LayerEditor.mock.mock_config as mockcfg
from LayerEditor.leconfig import cfg
import shutil
import os
import pytest

@pytest.mark.qt
def test_serialize_base(request, qapp):
    TEST_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_geometry_serialize")
    mockcfg.set_empty_config()
    cfg.init()

    if not os.path.isdir(TEST_DIR):
        os.makedirs(TEST_DIR)

    points = [[100, 100], [200, 200], [300, 100], [100, 200]]
    lines = [[0, 1], [1, 2], [2, 3], [3, 0]]
    
    cfg.le_serializer.set_new(cfg)
    diagram = cfg.diagram
    assert diagram.topology_owner

    # TODO:
    # Need to review and possibly fix diagram adding methods as they do not preserve consitency in Regions.
    # Remove hidden dependency of diagram.add_point on Qt.

    for point in points:
        diagram.add_point(point[0], point[1], 'Add test point', None, False)
    for line in lines:
        diagram.join_line(diagram.points[line[0]], diagram.points[line[1]], "Add test line", None, False)
        
    cfg.le_serializer.save(cfg, os.path.join(TEST_DIR, "test_geometry1.json"))
    
    cfg.le_serializer.set_new(cfg)
    cfg.le_serializer.load(cfg, os.path.join(TEST_DIR, "test_geometry1.json"))
    diagram2 = cfg.diagram 
 
    assert len(diagram.points)==len(diagram2.points)
    for i in range(0, len(diagram2.points)):
        assert diagram.points[i].x==diagram2.points[i].x
        assert diagram.points[i].y==diagram2.points[i].y
        
    assert len(diagram.lines)==len(diagram2.lines)
    for i in range(0, len(diagram2.lines)):
        assert diagram.points.index(diagram.lines[i].p1)==diagram2.points.index(diagram2.lines[i].p1)
        assert diagram.points.index(diagram.lines[i].p2)==diagram2.points.index(diagram2.lines[i].p2)

    shutil.rmtree(TEST_DIR, ignore_errors=True)
