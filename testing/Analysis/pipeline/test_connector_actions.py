from pipeline.connector_actions import *
from pipeline.generator_actions import *
from pipeline.convertors import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *
import pipeline.action_types as action
from .pomfce import *
import os

def test_connector_code_init():
    action.__action_counter__ = 0
    v1 = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    v2 = VariableGenerator(Variable=Struct(a=String("test new"), b=Int(8)))
    v3 = VariableGenerator(Variable=Ensemble(
            Struct(a=String(), time=Int(), value = Float(), bc_type=Int()),
            Struct(a=String("a1"), time=Int(500), value = Float(5.0), bc_type=Int(4)), 
            Struct(a=String("a2"), time=Int(650), value = Float(2.0), bc_type=Int(4)),
            Struct(a=String("a3"), time=Int(700), value = Float(8.0), bc_type=Int(3)),
            Struct(a=String("a4"), time=Int(750), value = Float(12.0), bc_type=Int(4)),
            Struct(a=String("a5"), time=Int(850), value = Float(2.0), bc_type=Int(3)),
            Struct(a=String("a6"), time=Int(900), value = Float(13.0), bc_type=Int(4)),
            Struct(a=String("a7"), time=Int(1100), value = Float(18.0), bc_type=Int(6))
        ))
    
    
    time = And(Input(0).time > 600,Input(0).time<1000)
    value = Or(Input(0).value > 3.0, Input(0).value < 1.0)
    bc_type = Input(0).bc_type == 4
    p1 = Predicate(And( time, value, bc_type)) 
    c1 = Comparator(Input(0).value) 
 
    k = Connector()    
    a = Input(0).a
    b = Input(1).b
    # for later using
    k3 = k.duplicate()    
    conv = Convertor(Struct(a=a, b=b, c=Input(2).sort(c1)))
    k.set_config(Convertor = conv)
    
    k2 = k.duplicate()
    k2.set_inputs([v1, v2, v3])
    v1._inicialize()
    v2._inicialize()
    v3._inicialize()
    k2._inicialize()
    
    test=v1._get_settings_script()
    test.extend(v2._get_settings_script())
    test.extend(v3._get_settings_script())
    test.extend(k2._get_settings_script())
    
    # test code generation
    compare_with_file(os.path.join("pipeline", "results", "convertor1.py"), test)
    exec ('\n'.join(test), globals())    
    
    CommonConvertor_8._inicialize()
    # test sorting
    test = CommonConvertor_8._get_output()._get_settings_script()
#    compare_with_file(os.path.join("pipeline", "results", "convertor2.py"), test)
#    
#    k3.set_config(DefOutput = Struct(a=a, b=b, c=k.input(2).select(p1)))
#    k3.set_inputs([v1, v2, v3])
#    # test select
#    k3._inicialize()
#    test = k3.get_output()._get_settings_script()
#    compare_with_file(os.path.join("pipeline", "results", "convertor3.py"), test)
#    
#    assert False
