from ui.data.diagram_structures import Diagram
from ui.data.diagram_serializer import DiagramSerializer
import shutil
import os

TEST_DIR = os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "test_geometry_serialize")

def test_serialize_base(request):
    if not os.path.isdir(TEST_DIR):
        os.makedirs(TEST_DIR)
    def fin_remove_test_dir():        
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    request.addfinalizer(fin_remove_test_dir)
    
    points = [[100, 100], [200, 200], [300, 100], [100, 200]]
    lines = [[0, 1], [1, 2], [2, 3], [3, 0]]
    diagram = Diagram()

    for point in points:
        diagram.add_point(point[0], point[1], 'Add test point', None, True)
    for line in lines:
        diagram.join_line(diagram.points[line[0]], diagram.points[line[1]], "Add test line", None, True)

    ser = DiagramSerializer(diagram)
    ser.save(os.path.join(TEST_DIR, "test_geometry1.json"))
    
    diagram2 = Diagram()
    ser = DiagramSerializer(diagram2)
    ser.load(os.path.join(TEST_DIR, 0,  "test_geometry1.json"))

    assert len(diagram.points)==len(diagram2.points)
    for i in range(0, len(diagram2.points)):
        assert diagram.points[i].x==diagram2.points[i].x
        assert diagram.points[i].y==diagram2.points[i].y
        
    assert len(diagram.lines)==len(diagram2.lines)
    for i in range(0, len(diagram2.lines)):
        assert diagram.points.index(diagram.lines[i].p1)==diagram2.points.index(diagram2.lines[i].p1)
        assert diagram.points.index(diagram.lines[i].p2)==diagram2.points.index(diagram2.lines[i].p2)
        
    assert os.path.join(TEST_DIR, "test_geometry1.json")==diagram.path
    assert diagram.path==diagram2.path        
