from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_pipeline_code_init():
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
    pipeline=Pipeline(ResultActions=[foreach])
    flow._output=String()
    pipeline._inicialize()    
    test=pipeline._get_settings_script()
    
    compare_with_file(os.path.join("pipeline", "results", "workflow1.py"), test)
    exec ('\n'.join(test), globals())
    assert Flow123d_3._variables['YAMLFile'] == flow._variables['YAMLFile']
    
    # test validation
    err = gen.validate()
    assert len(err)==0
 
    # check output types directly
    assert isinstance(gen._get_output(), Ensemble)
    assert isinstance(gen._get_output().subtype, Struct)
   
    
    assert isinstance(foreach._get_output(), Ensemble)
    assert isinstance(foreach._get_output().subtype, String)
    assert isinstance(workflow.bridge._get_output(), Struct)
    assert 'a' in workflow.bridge._get_output()
    assert 'b' in workflow.bridge._get_output()
    assert 'c' not in workflow.bridge._get_output()    
    assert isinstance(flow._get_output(), String)
    
    # test pipeline with more action where is side effect action in separate branch
    action.__action_counter__ = 0
    gen = RangeGenerator(Items=items)
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    workflow = Workflow()
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="test.yaml")
    side = Flow123dAction(Inputs=[vg], YAMLFile="test2.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
    pipeline = Pipeline(ResultActions=[foreach])
    flow._output = String()
    pipeline._inicialize()
    test = pipeline._get_settings_script()

    compare_with_file(os.path.join("pipeline", "results", "workflow2.py"), test)

    # test validation
    err = pipeline.validate()
    assert len(err) == 0

    # check output types directly
    assert isinstance(gen._get_output(), Ensemble)
    assert isinstance(gen._get_output().subtype, Struct)

    assert isinstance(foreach._get_output(), Ensemble)
    assert isinstance(foreach._get_output().subtype, String)
    assert isinstance(workflow.bridge._get_output(), Struct)
    assert 'a' in workflow.bridge._get_output()
    assert 'b' in workflow.bridge._get_output()
    assert 'c' not in workflow.bridge._get_output()
    assert isinstance(flow._get_output(), String)
