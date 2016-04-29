from pipeline.convertors import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *

def test_convertors_validation():
    v1 = VariableGenerator(Variable=Ensemble(
            Struct(a=String(), time=Int(), value = Float(), bc_type=Int()),
            Struct(a=String("a1"), time=Int(500), value = Float(5.0), bc_type=Int(4)), 
            Struct(a=String("a2"), time=Int(650), value = Float(2.0), bc_type=Int(4)),
            Struct(a=String("a3"), time=Int(700), value = Float(8.0), bc_type=Int(3)),
            Struct(a=String("a4"), time=Int(750), value = Float(12.0), bc_type=Int(4)),
            Struct(a=String("a5"), time=Int(850), value = Float(2.0), bc_type=Int(3)),
            Struct(a=String("a6"), time=Int(900), value = Float(13.0), bc_type=Int(4)),
            Struct(a=String("a7"), time=Int(1100), value = Float(18.0), bc_type=Int(6))
        ))   
    v1._inicialize()
    v2 = VariableGenerator(Variable=Ensemble(
            Struct(a=String(), time=Int(), value = Float()),
            Struct(a=String("a1"), time=Int(500), value = Float(5.0)), 
            Struct(a=String("a2"), time=Int(650), value = Float(2.0)),
            Struct(a=String("a3"), time=Int(700), value = Float(8.0)),
            Struct(a=String("a4"), time=Int(750), value = Float(12.0)),
            Struct(a=String("a5"), time=Int(850), value = Float(2.0)),
            Struct(a=String("a6"), time=Int(900), value = Float(13.0)),
            Struct(a=String("a7"), time=Int(1100), value = Float(18.0))
        ))   
    v2._inicialize()
    v3 = VariableGenerator(Variable=Ensemble(Struct(value=String())))
    v3._inicialize()
    v4 = VariableGenerator(Variable=Struct(value=String()))
    v4._inicialize()
    v5 = VariableGenerator(Variable=Ensemble(Struct(value=Struct(a=Int(0)))))
    v5._inicialize()
    v6 = VariableGenerator(Variable=Ensemble(Struct(a=Struct(a=Int(0)))))
    v6._inicialize()
    v7 = VariableGenerator(Variable=Struct(a=String("test"), b=Int(3)))
    v7._inicialize()
    v8 = VariableGenerator(Variable=Struct(a=String("test new"), b=Int(8)))
    v8._inicialize()
    
    time = And(Input(0).time > 600,Input(0).time<1000)
    value = Or(Input(0).value > 3.0, Input(0).value < 1.0)
    bc_type = Input(0).bc_type == 4
    pred = Predicate(And( time, value, bc_type)) 
    errs = pred._check_params([v1])
    assert len(errs)==0 
    errs = pred._check_params([v2])
    assert len(errs)==1 
    assert errs[0] == "Variable 'bc_type' is not assignated."
    pred = Predicate(And(Input(0).time > 600,Input(1).time<1000))
    errs = pred._check_params([v1, v2])
    assert len(errs)==1
    assert errs[0] == "Only Input(0) is permited in predicate"
    
    key = KeyConvertor(Input(0).value) 
    errs = key._check_params([v3])
    assert len(errs)==0 
    errs = key._check_params([v4])
    assert len(errs)==1
    assert errs[0] == 'Input structure for iterable convertors must be ListDTT'
    errs = key._check_params([v5])
    assert len(errs)==0 
    errs = key._check_params([v6])
    assert len(errs)==1     
    assert errs[0] == "Variable 'value' is not assignated."
    
    a = Input(0).a
    b = Input(1).b 
    conv = Convertor(Struct(a=a, b=b, c=Input(2).sort(key)))
    errs = conv._check_params([v7, v8, v1])
    assert len(errs)==0 
    errs = conv._check_params([v7, v8])
    assert len(errs)==1
    assert errs[0] == "Variable 'value' is not assignated."
    
 
