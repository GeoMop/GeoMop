from src.common.analysis import base as wf
from src.common.analysis import actions


@wf.workflow
def test_workflow1(a, b):
    c = actions.tuple(a).name("c")
    d = actions.tuple(a, b)
    e = actions.tuple(c, d)
    return e

@wf.workflow
def test_workflow2(f, g, h):
    i = actions.tuple(f, g, h)
    return i


