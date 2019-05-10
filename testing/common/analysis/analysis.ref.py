import common.analysis as wf


@wf.workflow
def test_workflow(a, b):
    c = wf.tuple(a).name("c")
    tuple_1 = wf.tuple(a, b)
    tuple_2 = wf.tuple(c, tuple_1)
    return tuple_2