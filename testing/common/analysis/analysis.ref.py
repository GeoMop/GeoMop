import common.analysis as wf


@wf.workflow
def test_list(self, a, b):
    self.c = [a]
    List_1 = [a, b]
    List_2 = [self.c, List_1]
    return List_2


@wf.Class
class Point:
    x:float
    y:float


@wf.workflow
def test_class(self, a, b):
    self.a_x = a.x
    self.b_y = b.y
    Point_1 = Point(x=self.a_x, y=self.b_y)
    return Point_1


@wf.analysis
def test_analysis(self):
    Value_1 = 10
    Value_2 = 'ahoj'
    self.tuple = test_list(a=Value_1, b=Value_2)
    Value_3 = 20
    Value_4 = 30
    Point_1 = Point(x=Value_3, y=Value_4)
    Value_5 = 40
    Value_6 = 50
    Point_2 = Point(x=Value_5, y=Value_6)
    self.point = test_list(a=Point_1, b=Point_2)
    List_1 = [self.tuple, self.point]
    return List_1