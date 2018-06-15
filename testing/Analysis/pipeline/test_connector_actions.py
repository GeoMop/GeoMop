from Analysis.pipeline.connector_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.convertors import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.generic_tree import *
import Analysis.pipeline.action_types as action
import Analysis.pipeline.convertors as convertor
from .pomfce import *
import os


this_source_dir = os.path.dirname(os.path.realpath(__file__))


def test_connector_code_init(change_dir_back):
    os.chdir(this_source_dir)

    action.__action_counter__ = 0
    convertor.__convertor_counter__ = 0
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
    c1 = KeyConvertor(Input(0).value) 
 
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
    compare_with_file(os.path.join("results", "convertor1.py"), test)
    
    test2 = k2._get_output()._get_settings_script()
    #check sorting result
    compare_with_file(os.path.join("results", "convertor2.py"), test2)
    
    # test generated code
    exec ('\n'.join(test), globals())   
    
    VariableGenerator_1._inicialize()
    VariableGenerator_2._inicialize()
    VariableGenerator_3._inicialize()
    Conn_6._inicialize()    
    # test sorting result from generate code
    test = Conn_6._get_output()._get_settings_script()
    compare_with_file(os.path.join("results", "convertor2.py"), test)
    
    assert VariableGenerator_1._get_hash() == v1._get_hash()
    assert VariableGenerator_2._get_hash() == v2._get_hash()
    assert VariableGenerator_3._get_hash() == v3._get_hash()
    assert Key_2._get_unique_text() == c1._get_unique_text()
    assert Conv_3._get_unique_text() == conv._get_unique_text()
    assert Conn_6._get_hash() == k2._get_hash()
    assert Conn_6._get_hash() != k._get_hash()
    
    k4 = k3.duplicate() 
    conv2 = Convertor(Struct(a=a, b=b, c=Input(2).select(p1)))
    k3.set_config(Convertor=conv2)
    k3.set_inputs([v1, v2, v3])
    # test select
    k3._inicialize()
    test = k3._get_output()._get_settings_script()
    compare_with_file(os.path.join("results", "convertor3.py"), test)
    
    adap = Adapter(Struct(a=Struct(a=Input(0).a), b=Struct(a=Input(0).value)))
    conv3 = Convertor(Struct(a=a, b=b, c=Input(2).each(adap)))
    k4.set_config(Convertor=conv3)
    k4.set_inputs([v1, v2, v3])
    # test each
    k4._inicialize()
    test = k4._get_output()._get_settings_script()
    compare_with_file(os.path.join("results", "convertor4.py"), test)
    
#    assert False
