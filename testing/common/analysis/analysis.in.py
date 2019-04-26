import common.analysis as wf


@wf.workflow
def test_workflow(a, b):
    c = wf.tuple(a).name("c")
    d = wf.tuple(a, b)
    e = wf.tuple(c, d)
    return e
