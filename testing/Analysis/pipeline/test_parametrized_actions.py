from pipeline.parametrized_actions import *
from pipeline.data_types_tree import *
import os

def compare_with_file(fname, lines):
    with open(fname) as f:
        res = f.readlines()
        i=0
        for line in res:
            if i==len(lines):
                assert False, \
                    "Line {0} is not in result\n{1}".format(str(i+1),line.rstrip())
                break
            assert line.rstrip() == lines[i].rstrip(), \
                "on line {0}\n{1}\n<>\n{2}".format(str(i+1),line.rstrip() ,lines[i].rstrip())
            i += 1
        assert i>=len(res), \
            "Line {0} is not in file\n{1}".format(str(i+1),lines[i].rstrip())
            
    

def test_flow_code_init():
    flow=Flow123dAction(Input=Struct(test1=String("test")), Output=String("File"), YAMLFile="test.yaml")
    test=flow.get_settings_script()
    compare_with_file(os.path.join("pipeline", "results", "flow1.txt"), test)
    exec ('\n'.join(test), globals())
    assert Flow123d_1.variables['YAMLFile'] == flow.variables['YAMLFile']
    # assert Flow123d_1.inputs[0].test == flow.inputs[0].test
    # assert Flow123d_1.outputs[0] == flow.outputs[0]
    
    
