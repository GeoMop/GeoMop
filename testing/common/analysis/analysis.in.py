import common.analysis as wf


@wf.workflow
def test_tuple(self, a, b):
    self.c = (a,)
    d = (a, b)
    e = (self.c, d)
    return e


@wf.Class
class Point:
    x:float
    y:float


@wf.workflow
def test_class(self, a: Point, b: Point):
    self.a_x = a.x
    self.b_y = b.y
    return Point(self.a_x, self.b_y)


@wf.analysis
def test_analysis(self):
    self.tuple = test_tuple(10, "ahoj")
    self.point = test_tuple(Point(20, 30), Point(40, 50))
    return (self.tuple, self.point)