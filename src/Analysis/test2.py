from pipeline.convertors import *
from pipeline.data_types_tree import *
from pipeline.generic_tree import *

v1 = VariableGenerator(Variable=Struct(
    a=Ensemble(Int(), Int(1), Int(2), Int(3)),
    b=String("b")
))
v1._inicialize()

a1 = Adapter(Struct(x=Input(0)))
a2 = Adapter(Input(0).x)
conv = Convertor(Input(0).a.each(a1).each(a2))
errs = conv._check_params([v1])
assert len(errs) == 0
