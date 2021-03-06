from Analysis.pipeline.parametrized_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.wrapper_actions import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.workflow_actions import *
from Analysis.pipeline.pipeline import *
from .pomfce import *
import Analysis.pipeline.action_types as action
import os


this_source_dir = os.path.dirname(os.path.realpath(__file__))


def test_workflow_code_init(request, change_dir_back):
    def clear_backup():
        pass
    request.addfinalizer(clear_backup)

    os.chdir(this_source_dir)

    # test workflow with more action
    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    workflow = Workflow(Inputs=[vg])
    f1 = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    f2 = Flow123dAction(Inputs=[f1], YAMLFile="resources/test2.yaml")
    workflow.set_config(OutputAction=f2, InputAction=f1)
    workflow._inicialize()
    vg._inicialize()
    f1._output = Struct()
    test = workflow._get_settings_script()

    compare_with_file(os.path.join("results", "workflow3.py"), test)

    # test validation
    err = workflow.validate()
    assert len(err) == 0

    # test _get_hashes_list()
    hlist = workflow._get_hashes_list()
    assert sorted(hlist.keys()) == ["2", "3", "4"]


    # test workflow with more action where is side effect action in separate branch
    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    side = Flow123dAction(Inputs=[vg], YAMLFile="resources/test2.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    flow._output = String()
    workflow._inicialize()
    vg2._inicialize()
    test = workflow._get_settings_script()

    compare_with_file(os.path.join("results", "workflow4.py"), test)

    # test validation
    err = workflow.validate()
    assert len(err) == 0

    # test _get_hashes_list()
    hlist = workflow._get_hashes_list()
    assert sorted(hlist.keys()) == ["1", "3", "4", "5"]


    # test workflow duplication
    action.__action_counter__ = 0
    workflow = Workflow()
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow)
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    w1 = workflow.duplicate()
    w1.set_inputs([vg])
    w2 = workflow.duplicate()
    w2.set_inputs([w1])
    pipeline = Pipeline(ResultActions=[w2])
    pipeline._inicialize()
    test = pipeline._get_settings_script()

    compare_with_file(os.path.join("results", "workflow5.py"), test)

    # test validation
    err = pipeline.validate()
    assert len(err) == 0

    # test _get_hashes_list()
    hlist = pipeline._get_hashes_list()
    assert sorted(hlist.keys()) == ["3", "4", "5", "6", "7", "8"]


    # test workflow v 2xForEach in each other
    action.__action_counter__ = 0
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True}
    ]
    items2 = [
        {'name': 'x', 'value': 1, 'step': 0.1, 'n_plus': 1, 'n_minus': 1, 'exponential': False},
        {'name': 'y', 'value': 10, 'step': 1, 'n_plus': 2, 'n_minus': 0, 'exponential': True}
    ]
    gen = RangeGenerator(Items=items)
    gen2 = RangeGenerator(Items=items2)
    workflow = Workflow()
    workflow2 = Workflow()
    flow = Flow123dAction(Inputs=[workflow2.input()], YAMLFile="resources/test1.yaml")
    workflow2.set_config(OutputAction=flow, InputAction=flow)
    foreach2 = ForEach(Inputs=[gen2], WrappedAction=workflow2)
    workflow.set_config(OutputAction=foreach2, InputAction=foreach2)
    foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
    pipeline = Pipeline(ResultActions=[foreach])
    flow._output = String()
    pipeline._inicialize()
    test = pipeline._get_settings_script()

    compare_with_file(os.path.join("results", "workflow6.py"), test)

    # test validation
    err = pipeline.validate()
    assert len(err) == 0

    # test _get_hashes_list()
    hlist = pipeline._get_hashes_list()
    assert sorted(hlist.keys()) == ["1", "2", "3", "4", "5", "6", "7", "8"]


    # test workflow with one direct input
    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    workflow = Workflow(Inputs=[vg])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow)
    workflow._inicialize()
    vg._inicialize()
    test = workflow._get_settings_script()

    compare_with_file(os.path.join("results", "workflow7.py"), test)

    # test validation
    err = workflow.validate()
    assert len(err) == 0

    # test _get_hashes_list()
    hlist = workflow._get_hashes_list()
    assert sorted(hlist.keys()) == ["2", "3"]


    # test comparation of workflow hash
    action.__action_counter__ = 0
    workflow = Workflow()
    f1 = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    f2 = Flow123dAction(Inputs=[f1], YAMLFile="resources/test2.yaml")
    workflow.set_config(OutputAction=f2, InputAction=f1)
    workflow._inicialize()

    workflow2 = Workflow()
    f12 = Flow123dAction(Inputs=[workflow2.input()], YAMLFile="resources/test1.yaml")
    f22 = Flow123dAction(Inputs=[f12], YAMLFile="resources/test2.yaml")
    workflow2.set_config(OutputAction=f22, InputAction=f12)
    workflow2._inicialize()

    assert workflow._get_hash() == workflow2._get_hash()
