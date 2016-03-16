from pipeline.data_types_tree import *
from pipeline.generator_actions import *

output = Ensemble(Struct(a=Int(1), b=Int(10)))
items = [
    {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
    {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':3,'exponential':True} 
]
gen=RangeGenerator(Items=items, Output=output)
err = gen.validate()
test=gen.run()

for out in gen.output:
    out2=out

res = "\n".join(test)
i=1



