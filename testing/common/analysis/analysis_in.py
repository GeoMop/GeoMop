import src.common.analysis as wf


@wf.workflow
def test_list(self, a, b):
    self.c = [a]
    d = [a, b]
    e = [self.c, d]
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
    self.tuple = test_list(10, "ahoj")
    self.point = test_list(Point(20, 30), Point(40, 50))
    return [self.tuple, self.point]

"""
TODO:
- rethink organisation, move public stuff
- remove data.py
- finish test debugging
- improve exception forwarding form exec
- distinct errors for system (asserts), actions impl., workflow
- specific report of workflow errors (line, problem type)
- set_input check and exception when loading out of GUI

FUTURE:
- possibly have different actions as instances of few base classes carring just
  different evaluate functions. Separate class only if code mechanism is substantialy different.
  e.g. GenericAction, ListAction, OperatorAction, MetaAction (workflow, foreach, while, ..)
- have another object to keep arguments, ... connection within workflow 
- Resources:
    latency, speed, tags (supported features, HW, SW)  
"""