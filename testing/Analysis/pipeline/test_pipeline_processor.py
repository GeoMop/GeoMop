from pipeline.connector_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *
from pipeline.convertors import *
from pipeline.pipeline_processor import *
from pipeline.pipeline import *
from pipeline.workflow_actions import *
from pipeline.wrapper_actions import *
from pipeline.parametrized_actions import *
import pipeline.action_types as action
import time

def test_run_pipeline():
    action.__action_counter__ = 0
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
    ]
    gen = RangeGenerator(Items=items)    
    workflow=Workflow()
    flow=Flow123dAction(Inputs=[workflow.input()], YAMLFile="test.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow)
    foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
    ForEach._import_string =  "from pipeline import *\n"
    pipeline=Pipeline(ResultActions=[foreach])
    pipeline._inicialize()
    pp = Pipelineprocessor(pipeline)
    errs = pp.validate()
    
    assert len(errs)==0

    names = []
    pp.run()
    i = 0
    
    while pp.is_run():
        runner = pp.get_next_job()
        if runner is None:
            time.sleep(0.1)
        else:
            names.append(runner.name)
            pp.set_job_finished(runner.id)
        i += 1
        assert i<1000, "Timeout"   
        
    assert len(names) == 5
    assert names[0][:8] == 'Flow123d'
    assert names[1][:8] == 'Flow123d'
    assert names[2][:8] == 'Flow123d'
    assert names[3][:8] == 'Flow123d'
    assert names[4][:8] == 'Flow123d'
    # ToDo add more asserts after Flow123dAction finishing
    
# ToDo: Test invalid pipeline (cyclic dependencies in pipeline and workflow)
# ToDo: Test pipeline with all types of convertors
