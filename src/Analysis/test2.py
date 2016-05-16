from pipeline.convertors import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *
    
v1 = VariableGenerator(Variable=Struct(
        a=Ensemble(Int(), Int(1), Int(2), Int(3)), b=String("b")
    ))
v1._inicialize()

# each()
adap = Adapter(Struct(x=Input(0)))
conv = Convertor(Struct(a=Input(0).a.each(adap)))
errs = conv._check_params([v1])
assert len(errs) == 0

# sort
v1 = VariableGenerator(Variable=Ensemble(
        Sequence(Int()),
        Sequence(Int(), Int(4), Int(8), Int(2)),
        Sequence(Int(), Int(3), Int(2), Int(1))
    ))
#v1 = VariableGenerator(Variable=Sequence(Int(), Int(4), Int(8), Int(2)))
v1._inicialize()

kc1 = KeyConvertor(Input(0))
kc2 = KeyConvertor(Input(0).sort(kc1).tail())
c = Convertor(Input(0).sort(kc2))
errs = c._check_params([v1])
assert len(errs) == 0
