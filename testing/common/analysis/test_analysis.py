from common.analysis import workflow as wf
from common.analysis import actions


def test_generic_representation():

    @wf.workflow
    def test_workflow(a, b):
        c = actions.Tuple(a).name("c")
        d = actions.Tuple(a, b)
        e = actions.Tuple(c, d)
        return e

    ref =\
    """def test_workflow(a, b):
    c = Tuple(a)
    Tuple_1 = Tuple(a, b)
    Tuple_2 = Tuple(c, Tuple_1)
    return Tuple_2"""
    assert ref == test_workflow.code()

# TODO: deal with correct module (action.Tuple)
# TODO: have test cases as input files, check agains input code