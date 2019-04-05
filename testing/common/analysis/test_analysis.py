from common.analysis import workflow
from common.analysis import actions

def test_generic_representation():


    def test_workflow(a, b):
        c = actions.Tuple(a).name("c")
        d = actions.Tuple(a, b)
        e = actions.Tuple(c, d)
        return e

    w = workflow.make_workflow(test_workflow)
    print(w.code())