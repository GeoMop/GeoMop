from pipeline.covertor_actions import *
from pipeline.data_types_tree import *
import os

def test_convertor_code_init():
    p1 = Predicate(Inputs=[GDTT(Struct)]) 
    time = p.input[0].time > 600 and p.input[0].time<1000
    value = p.input[0].value > 3.0 or k.input[0].value < 1.0
    bc_type = p.input[0].bc_type == 4
    p1.output (time and value and bc_type)
    
    p2 = Predicate(Inputs=[GDTT(Struct), GDTT(Struct)]) 
    p2.output (time1 > time2)
    
    k = CommonConverter(Inputs=[GDTT(Struct), GDTT(Struct), GDTT(Ensemble)])    
    a = k.input[0].a
    b = k.input[1].b
    c = p2.sort(k.input[2])[0].a
    d = p1.select(k.input[2])
    k.output = Struc(a, b, c, d)
    
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
            Struct(a=String("a7"), time=Int(1100), value = Float(18.0), bc_type=Int(6)),
        ))
        
    k2 =k.duplicate() 
    k2.set_inputs([v1, v2, v3])
    v1.inicialize()
    v2.inicialize()
    v3.inicialize()
    k2.inicialize()
    
    compare_with_file(os.path.join("pipeline", "results", "convertor1.py"), test)
    exec ('\n'.join(test), globals())
