from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_flow_code_init():
    action.__action_counter__ = 0
    input=VariableGenerator(Variable=Struct(test1=String("test")))
    input._inicialize()
    flow=Flow123dAction(Inputs=[input], YAMLFile="test.yaml")
    flow._inicialize()    
    test = input._get_settings_script()
    test.extend(flow._get_settings_script())

    compare_with_file(os.path.join("pipeline", "results", "flow1.py"), test)
    exec ('\n'.join(test), globals())
    VariableGenerator_1._inicialize()
    Flow123d_2._inicialize()    
    
    assert Flow123d_2._variables['YAMLFile'] == flow._variables['YAMLFile']
    assert Flow123d_2.get_input_val(0).test1 == flow.get_input_val(0).test1
    assert Flow123d_2._get_hash() == flow._get_hash()


def test_flow_runner_command(request):
    def clear_backup():
        if os.path.isfile("pipeline/resources/test1_param.yaml"):
            os.remove("pipeline/resources/test1_param.yaml")
    request.addfinalizer(clear_backup)

    action.__action_counter__ = 0
    vg = VariableGenerator(Variable=Struct())
    flow = Flow123dAction(Inputs=[vg], YAMLFile="pipeline/resources/test1.yaml")

    vg._inicialize()
    flow._inicialize()
    err = flow.validate()
    assert len(err) == 0

    runner = flow._update()
    assert runner.command == ["flow123d", "-s", os.path.join("pipeline/resources", "test1_param.yaml")]
