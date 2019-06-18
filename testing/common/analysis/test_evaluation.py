import pytest
import common.analysis as analysis
import common.analysis.evaluation as evaluation
#import common.analysis.action_workflow as wf
#import common.analysis.action_base as base

@pytest.mark.parametrize("src_file", ["analysis_in.py"])
def test_evaluation(src_file):
    module = analysis.module.Module(src_file)
    wf_test_class = module.get_workflow(name='test_class')
    Point = module.get_workflow(name='Point')
    pa = Point.constructor(x=0, y=1)
    pb = Point.constructor(x=2, y=3)


    eval = evaluation.Evaluation()
    results = eval.execute_workflow(wf_test_class, [pa, pb])



