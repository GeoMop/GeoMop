from Analysis.pipeline.parametrized_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.wrapper_actions import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.workflow_actions import *
from Analysis.pipeline.pipeline import *
from Analysis.pipeline.identical_list import *
from .pomfce import *
import Analysis.pipeline.action_types as action
import os

this_source_dir = os.path.dirname(os.path.realpath(__file__))
def data_file(test_path):
    return os.path.join(this_source_dir, "resources", test_path)


def test_pipeline_code_init(request):
    def clear_backup():
        pass
    request.addfinalizer(clear_backup)

    action.__action_counter__ = 0
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
    ]
    gen = RangeGenerator(Items=items)    
    workflow=Workflow()
    flow=Flow123dAction(Inputs=[workflow.input()], YAMLFile=data_file("test1.yaml"))
    workflow.set_config(OutputAction=flow, InputAction=flow)
    foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
    pipeline=Pipeline(ResultActions=[foreach])
    flow._output=String()
    pipeline._inicialize()
    test=pipeline._get_settings_script()
    
#    compare_with_file(os.path.join("pipeline", "results", "workflow1.py"), test)
#    exec ('\n'.join(test), globals())
#    assert Flow123d_3._variables['YAMLFile'] == flow._variables['YAMLFile']
    
    # test validation
    err = gen.validate()
    assert len(err)==0
 
    # check output types directly
    assert isinstance(gen._get_output(), Ensemble)
    assert isinstance(gen._get_output().subtype, Struct)
   
    
    assert isinstance(foreach._get_output(), Ensemble)
    assert isinstance(foreach._get_output().subtype, Struct)
    assert isinstance(workflow.bridge._get_output(), Struct)
    assert 'a' in workflow.bridge._get_output()
    assert 'b' in workflow.bridge._get_output()
    assert 'c' not in workflow.bridge._get_output()    
    assert isinstance(flow._get_output(), Struct)
    
    # test pipeline with more action where is side effect action in separate branch
    action.__action_counter__ = 0
    gen = RangeGenerator(Items=items)
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    workflow = Workflow()
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile=data_file("test1.yaml"))
    side = Flow123dAction(Inputs=[vg], YAMLFile=data_file("test2.yaml"))
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
    pipeline = Pipeline(ResultActions=[foreach])
    flow._output = String()
    pipeline._inicialize()
    test = pipeline._get_settings_script()

    # TODO: Serialization to the script has to be always to particular file and
    # all internall file paths has to be converted to relative paths.
    # Moreover pipeline should support operation that pass through all actions and translates their paths.
    compare_with_file("workflow2.py", test)

    # test validation
    err = pipeline.validate()
    assert len(err) == 0

    # check output types directly
    assert isinstance(gen._get_output(), Ensemble)
    assert isinstance(gen._get_output().subtype, Struct)

    assert isinstance(foreach._get_output(), Ensemble)
    assert isinstance(foreach._get_output().subtype, Struct)
    assert isinstance(workflow.bridge._get_output(), Struct)
    assert 'a' in workflow.bridge._get_output()
    assert 'b' in workflow.bridge._get_output()
    assert 'c' not in workflow.bridge._get_output()
    assert isinstance(flow._get_output(), Struct)


def test_hashes(request):
    def clear_backup():
        pass
    request.addfinalizer(clear_backup)

    # first pipeline
    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile=data_file("test1.yaml"))
    side = Flow123dAction(Inputs=[vg], YAMLFile=data_file("test2.yaml"))
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    pipeline = Pipeline(ResultActions=[workflow])
    pipeline._inicialize()
    test = pipeline._get_settings_script()
    hlist1 = pipeline._get_hashes_list()

    # second pipeline
    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test3"), b=Int(8)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile=data_file("test1.yaml"))
    side = Flow123dAction(Inputs=[vg], YAMLFile=data_file("test2.yaml"))
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    pipeline = Pipeline(ResultActions=[workflow])
    pipeline._inicialize()
    test = pipeline._get_settings_script()
    hlist2 = pipeline._get_hashes_list()

    # hashes comparison
    assert hlist1["1"] == hlist2["1"]
    assert hlist1["2"] != hlist2["2"]
    assert hlist1["3"] != hlist2["3"]
    assert hlist1["4"] != hlist2["4"]
    assert hlist1["5"] == hlist2["5"]
    assert hlist1["6"] != hlist2["6"]


def test_set_restore_id(request):
    def clear_backup():
        pass
    request.addfinalizer(clear_backup)

    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile=data_file("test1.yaml"))
    side = Flow123dAction(Inputs=[vg], YAMLFile=data_file("test2.yaml"))
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    pipeline = Pipeline(ResultActions=[workflow])

    il = IdenticalList({"1": "11", "2": "12", "3": "13", "4": "14"})
    pipeline._set_restore_id(il)

    assert vg._restore_id == "11"
    assert vg2._restore_id == "12"
    assert workflow._restore_id == "13"
    assert flow._restore_id == "14"
    assert side._restore_id is None
    assert pipeline._restore_id is None
