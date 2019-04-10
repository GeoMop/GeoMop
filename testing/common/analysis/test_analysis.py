from common.analysis import workflow as wf
from common.analysis import actions


def test_generic_representation():

    @wf.workflow
    def test_workflow(a, b):
        c = actions.Tuple(a).name("c")
        d = actions.Tuple(a, b)
        e = actions.Tuple(c, d)
        return e

    print(test_workflow.code())