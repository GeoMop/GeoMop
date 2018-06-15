from Analysis.pipeline.connector_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.generic_tree import *
from Analysis.pipeline.convertors import *
from Analysis.pipeline.pipeline_processor import *
from Analysis.pipeline.pipeline import *
from Analysis.pipeline.workflow_actions import *
from Analysis.pipeline.wrapper_actions import *
from Analysis.pipeline.parametrized_actions import *
import Analysis.pipeline.action_types as action
from Analysis.client_pipeline.identical_list_creator import *
from .pomfce import *
import time
import shutil
import pytest


this_source_dir = os.path.dirname(os.path.realpath(__file__))


@pytest.mark.slow
def test_run_pipeline(request, change_dir_back):
    def clear_backup():
        shutil.rmtree("backup", ignore_errors=True)
        remove_if_exist(os.path.join("resources", "test1_3_0.yaml"))
        remove_if_exist(os.path.join("resources", "test1_3_1.yaml"))
        remove_if_exist(os.path.join("resources", "test1_3_2.yaml"))
        remove_if_exist(os.path.join("resources", "test1_3_3.yaml"))
        remove_if_exist(os.path.join("resources", "test1_3_4.yaml"))
    request.addfinalizer(clear_backup)

    os.chdir(this_source_dir)

    action.__action_counter__ = 0
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
    ]
    gen = RangeGenerator(Items=items)    
    workflow=Workflow()
    flow=Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow)
    foreach = ForEach(Inputs=[gen], WrappedAction=workflow)
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
    
    # test store file names
    assert os.path.isdir(os.path.join("backup", "store"))
    assert os.path.isdir(os.path.join("backup", "restore"))
    assert len(os.listdir(os.path.join("backup", "store")))==11
    assert len(os.listdir(os.path.join("backup", "restore")))==0
    assert os.path.isfile(os.path.join("backup", "store", "ForEach_4"))
    assert os.path.isfile(os.path.join("backup", "store", "Workflow_2_0"))
    assert os.path.isfile(os.path.join("backup", "store", "Workflow_2_1"))
    assert os.path.isfile(os.path.join("backup", "store", "Workflow_2_2"))
    assert os.path.isfile(os.path.join("backup", "store", "Workflow_2_3"))
    assert os.path.isfile(os.path.join("backup", "store", "Workflow_2_4"))
    assert os.path.isfile(os.path.join("backup", "store", "Flow123d_3_0"))
    assert os.path.isfile(os.path.join("backup", "store", "Flow123d_3_1"))
    assert os.path.isfile(os.path.join("backup", "store", "Flow123d_3_2"))
    assert os.path.isfile(os.path.join("backup", "store", "Flow123d_3_3"))
    assert os.path.isfile(os.path.join("backup", "store", "Flow123d_3_4"))
    
    pp. _establish_processing(None)
    
    assert os.path.isdir(os.path.join("backup", "store"))
    assert os.path.isdir(os.path.join("backup", "restore"))
    assert len(os.listdir(os.path.join("backup", "store")))==0
    assert len(os.listdir(os.path.join("backup", "restore")))==11
    assert os.path.isfile(os.path.join("backup", "restore", "ForEach_4"))
    
    # ToDo add more asserts after Flow123dAction finishing
    
# ToDo: Test invalid pipeline (cyclic dependencies in pipeline and workflow)
# ToDo: Test pipeline with all types of convertors


def test_set_restore_id(request, change_dir_back):
    def clear_backup():
        shutil.rmtree("backup", ignore_errors=True)
    request.addfinalizer(clear_backup)

    os.chdir(this_source_dir)

    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    side = Flow123dAction(Inputs=[vg], YAMLFile="resources/test2.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    pipeline = Pipeline(ResultActions=[workflow])

    pp = Pipelineprocessor(pipeline, identical_list=os.path.join(
        "resources", "identical_list.json"))

    assert vg._restore_id == "11"
    assert vg2._restore_id == "12"
    assert workflow._restore_id == "13"
    assert flow._restore_id == "14"
    assert side._restore_id is None
    assert pipeline._restore_id is None


def test_hashes_and_store_restore(request, change_dir_back):
    def clear_backup():
        shutil.rmtree("backup", ignore_errors=True)
        remove_if_exist("identical_list.json")
        remove_if_exist(os.path.join("resources", "test1_4.yaml"))
        remove_if_exist(os.path.join("resources", "test2_5.yaml"))
    request.addfinalizer(clear_backup)

    os.chdir(this_source_dir)

    # create pipeline first time
    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    side = Flow123dAction(Inputs=[vg], YAMLFile="resources/test2.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    pipeline = Pipeline(ResultActions=[workflow])

    pp = Pipelineprocessor(pipeline)
    errs = pp.validate()
    assert len(errs) == 0

    hlist1 = pp._pipeline._get_hashes_list()

    pp.run()
    i = 0
    while pp.is_run():
        runner = pp.get_next_job()
        if runner is None:
            time.sleep(0.1)
        else:
            pp.set_job_finished(runner.id)
        i += 1
        assert i < 1000, "Timeout"

    assert os.path.isdir(os.path.join("backup", "store"))
    assert os.path.isdir(os.path.join("backup", "restore"))
    assert len(os.listdir(os.path.join("backup", "store"))) == 2
    assert len(os.listdir(os.path.join("backup", "restore"))) == 0

    # create pipeline second time
    vg = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    vg2 = VariableGenerator(Variable=Struct(a=String("test2"), b=Int(5)))
    workflow = Workflow(Inputs=[vg2])
    flow = Flow123dAction(Inputs=[workflow.input()], YAMLFile="resources/test1.yaml")
    side = Flow123dAction(Inputs=[vg], YAMLFile="resources/test2.yaml")
    workflow.set_config(OutputAction=flow, InputAction=flow, ResultActions=[side])
    pipeline = Pipeline(ResultActions=[workflow])
    pipeline._inicialize()

    hlist2 = pipeline._get_hashes_list()

    il = ILCreator.create_identical_list(hlist2, hlist1)
    il.save("identical_list.json")

    pp = Pipelineprocessor(pipeline, identical_list="identical_list.json")
    errs = pp.validate()
    assert len(errs) == 0

    pp.run()
    i = 0
    while pp.is_run():
        runner = pp.get_next_job()
        if runner is None:
            time.sleep(0.1)
        else:
            pp.set_job_finished(runner.id)
        i += 1
        assert i < 1000, "Timeout"

    assert flow._restore_id is not None
    assert side._restore_id is not None
