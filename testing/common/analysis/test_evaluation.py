import pytest
from common.analysis import module
import common.analysis.evaluation as evaluation
from common.analysis import task
#import common.analysis.action_base as base

@pytest.mark.parametrize("src_file", ["analysis_in.py"])
def test_evaluation(src_file):
    mod = module.Module(src_file)
    wf_test_class = mod.get_workflow(name='test_class')
    assert sorted(list(wf_test_class._actions.keys())) == ['Point_1', '__result__', 'a', 'a_x', 'b', 'b_y']
    Point = mod.get_workflow(name='Point')
    pa = Point.constructor(x=0, y=1)
    pb = Point.constructor(x=2, y=3)

    # TODO: support for argument binding in the code wrapper.
    # Implement it as a function that creates a bind workflow consisting of the
    # binded action and few Value action instances.
    # Then make_analysis (which binds all parameters) can be replaced this more general feature.
    analysis = evaluation.Evaluation.make_analysis(wf_test_class, [pa, pb])
    assert sorted(list(analysis._actions.keys())) == ['Value_1', 'Value_2', '__result__', 'test_class_1']
    eval = evaluation.Evaluation(analysis)
    result = eval.execute()

    assert isinstance(result, task.Composed)
    assert isinstance(result.result, Point._data_class)
    assert result.result.x == 0
    assert result.result.y == 3

    # first level workflow
    assert result.action == analysis
    assert result.child('Value_1').action.value == pa
    test_wf_task = result.child('test_class_1')

    # second level workflow
    assert test_wf_task.action == wf_test_class
    assert test_wf_task.child('a').result.x == 0
    assert test_wf_task.child('a').result.y == 1
    assert test_wf_task.child('b').result.x == 2
    assert test_wf_task.child('b').result.y == 3



