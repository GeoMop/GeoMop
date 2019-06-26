import pytest
from common.analysis import module
import common.analysis.evaluation as evaluation
#import common.analysis.action_workflow as wf
#import common.analysis.action_base as base

@pytest.mark.parametrize("src_file", ["analysis_in.py"])
def test_evaluation(src_file):
    mod = module.Module(src_file)
    wf_test_class = mod.get_workflow(name='test_class')
    Point = mod.get_workflow(name='Point')
    pa = Point.constructor(x=0, y=1)
    pb = Point.constructor(x=2, y=3)

    # TODO: support for argument binding in the code wrapper.
    # Implement it as a function that creates a bind workflow consisting of the
    # binded action and few Value action instances.
    # Then make_analysis (which binds all parameters) can be replaced this more general feature.
    analysis = evaluation.Evaluation.make_analysis(wf_test_class, [pa, pb])
    eval = evaluation.Evaluation(analysis)
    result = eval.execute()
    print(result.result)


