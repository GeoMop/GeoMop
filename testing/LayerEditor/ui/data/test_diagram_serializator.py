from ui.data.diagram_structures import Diagram
from ui.data.history import GlobalHistory
from ui.data.le_serializer import LESerializer
import mock_config as mockcfg
from leconfig import cfg
import shutil
import os

TEST_DIR = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "test_geometry_serialize")
mockcfg.set_empty_config()

def test_serialize_base(request):    
    if not os.path.isdir(TEST_DIR):
        os.makedirs(TEST_DIR)
    def fin_remove_test_dir():        
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    request.addfinalizer(fin_remove_test_dir)
    
    ser = LESerializer(cfg)
    points = [[100, 100], [200, 200], [300, 100], [100, 200]]
    lines = [[0, 1], [1, 2], [2, 3], [3, 0]]
    diagram = cfg.diagram
    
    for point in points:
        diagram.add_point(point[0], point[1], 'Add test point', None, True)
    for line in lines:
        diagram.join_line(diagram.points[line[0]], diagram.points[line[1]], "Add test line", None, True)   
        
    ser.save(cfg, os.path.join(TEST_DIR, "test_geometry1.json"))
    history = GlobalHistory()
    
    cfg.diagrams = [Diagram(history)]
    cfg.diagram = cfg.diagrams[0]
    
    ser = LESerializer(cfg)
    ser.load(cfg, os.path.join(TEST_DIR, "test_geometry1.json"))
    diagram2 = cfg.diagram 
 
    assert len(diagram.points)==len(diagram2.points)
    for i in range(0, len(diagram2.points)):
        assert diagram.points[i].x==diagram2.points[i].x
        assert diagram.points[i].y==diagram2.points[i].y
        
    assert len(diagram.lines)==len(diagram2.lines)
    for i in range(0, len(diagram2.lines)):
        assert diagram.points.index(diagram.lines[i].p1)==diagram2.points.index(diagram2.lines[i].p1)
        assert diagram.points.index(diagram.lines[i].p2)==diagram2.points.index(diagram2.lines[i].p2)       

