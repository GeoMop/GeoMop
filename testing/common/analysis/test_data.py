import src.common.analysis.data as data

@data.Class
class Point:
    x: float = 0.0
    y: float = 0.0

@data.Class
class Element:
    node_ids: data.List[int] = []
    region: int

@data.Class
class Mesh:
    nodes: data.List[Point] = []
    elements: data.List[Element] = []


def test_classtypes():
    mesh = Mesh()
    
    point = data.Class(x:float = 0, y:float = 0)
def test_subtypes():

    data.Sequence[]
