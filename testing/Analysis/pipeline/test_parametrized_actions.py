from Analysis.pipeline.parametrized_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.pipeline_processor import *
from Analysis.pipeline.pipeline import *
from .pomfce import *
import Analysis.pipeline.action_types as action
import os
import math


this_source_dir = os.path.dirname(os.path.realpath(__file__))

def data_file(test_path):
    return os.path.join(this_source_dir, "resources", test_path)



def test_flow_code_init():
    action.__action_counter__ = 0
    input=VariableGenerator(Variable=Struct(test1=String("test")))
    input._inicialize()
    flow=Flow123dAction(Inputs=[input], YAMLFile="test.yaml")
    flow._inicialize()    
    test = input._get_settings_script()
    test.extend(flow._get_settings_script())

    compare_with_file("flow1.py", test)
    exec ('\n'.join(test), globals())
    VariableGenerator_1._inicialize()
    Flow123d_2._inicialize()    
    
    assert Flow123d_2._variables['YAMLFile'] == flow._variables['YAMLFile']
    assert Flow123d_2.get_input_val(0).test1 == flow.get_input_val(0).test1
    assert Flow123d_2._get_hash() == flow._get_hash()


def test_flow_runner_command(request):
    def clear_backup():
        remove_if_exist(data_file("test1_2.yaml"))
    request.addfinalizer(clear_backup)

    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct())
    flow = Flow123dAction(Inputs=[vg], YAMLFile=data_file("test1.yaml"))

    vg._inicialize()
    flow._inicialize()
    err = flow.validate()
    assert len(err) == 0

    runner = flow._update()
    assert runner.command == ["flow123d", "-s", data_file("test1_2.yaml"),
                              "-o", os.path.join("output", "2")]


def test_function_action(request):
    def clear_test_files():
        shutil.rmtree("backup", ignore_errors=True)
    request.addfinalizer(clear_test_files)

    # pipeline
    var = Struct(x1=Float(1.0), x2=Float(2.0), x3=Float(math.pi/2))
    gen = VariableGenerator(Variable=var)
    fun = FunctionAction(
        Inputs=[gen],
        Params=["x1", "x2", "x3"],
        Expressions=["y1 = 2 * x1 + 3 * x2", "y2 = sin(x3)"])
    pipeline = Pipeline(ResultActions=[fun])

    # pipeline processor
    pp = Pipelineprocessor(pipeline)

    # validation
    err = pp.validate()
    assert len(err) == 0

    # run pipeline
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

    # check result
    assert fun._output.y1 == 8.0
    assert fun._output.y2 == 1.0
