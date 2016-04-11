from pipeline.generator_actions import *
from pipeline.data_types_tree import *
from .pomfce import *
import pipeline.action_types as action
import os

def test_generator_code_init():
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':3,'exponential':True} 
    ]
    action.__action_counter__ = 0
    #init generator
    gen=RangeGenerator(Items=items)
    gen.inicialize()
    test=gen.get_settings_script()
    compare_with_file(os.path.join("pipeline", "results", "gen1.py"), test)
    # generator by exec
    exec ('\n'.join(test), globals())
    
    #compare exec and init
    for i in range(0, 2): 
        assert RangeGenerator_1.variables['Items'][i]['name'] == gen.variables['Items'][i]['name']
        assert RangeGenerator_1.variables['Items'][i]['value'] == gen.variables['Items'][i]['value']
        assert RangeGenerator_1.variables['Items'][i]['step'] == gen.variables['Items'][i]['step']
        assert RangeGenerator_1.variables['Items'][i]['n_plus'] == gen.variables['Items'][i]['n_plus']
        assert RangeGenerator_1.variables['Items'][i]['n_minus'] == gen.variables['Items'][i]['n_minus']
    assert RangeGenerator_1.variables['Items'][1]['exponential'] == gen.variables['Items'][1]['exponential']
    
    RangeGenerator_1.inicialize()
    assert RangeGenerator_1.output.subtype.a == gen.output.subtype.a
    assert RangeGenerator_1.output.subtype.b == gen.output.subtype.b
    
    # test validation
    err = gen.validate()
    gen=RangeGenerator(Items=items)
    gen.inicialize()
    # valid output
    err = gen.validate()
    assert len(err)==0
    
    #without output
    action.__action_counter__ = 0
    gen=RangeGenerator(Items=items)
    gen.inicialize()
    err = gen.validate()
    assert len(err)==0    
    assert isinstance(gen.output.subtype.a, Float)
    assert isinstance(gen.output.subtype.b, Float)
    
    #range generation
    assert gen. run() == None
    i=0
    for out in gen.output:
        if i== 0:
            assert out.a == 1
            assert out.b == 10
        elif i== 1:
            assert out.a == 1.1
            assert out.b == 10
        elif i== 2:
            assert out.a == 0.9
            assert out.b == 10
        elif i== 3:
            assert out.a == 1
            assert out.b == 11
        elif i== 4:
            assert out.a == 1
            assert out.b.value == 12
        elif i== 5:
            assert out.a == 1
            assert out.b == 9
        elif i== 6:
            assert out.a == 1
            assert out.b == 8
        elif i== 7:
            assert out.a == 1
            assert out.b == 6
        i += 1
    assert i==8
    
    #all variants
    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0,'exponential':True} 
    ]
    gen=RangeGenerator(Items=items, AllCases=True)
    gen.inicialize()
    err = gen.validate()
    assert len(err)==0    
    assert isinstance(gen.output.subtype.a, Float)
    assert isinstance(gen.output.subtype.b, Float)
    
    #range generation
    assert gen. run() == None
    i=0
    for out in gen.output:
        if i== 0:
            assert out.a == 1
            assert out.b == 10
        elif i== 1:
            assert out.a == 1.1
            assert out.b == 10
        elif i== 2:
            assert out.a == 0.9
            assert out.b == 10
        elif i== 3:
            assert out.a == 1
            assert out.b == 11
        elif i== 4:
            assert out.a == 1
            assert out.b.value == 12
        elif i== 5:
            assert out.a == 1.1
            assert out.b == 11
        elif i== 6:
            assert out.a == 1.1
            assert out.b == 12
        elif i== 7:
            assert out.a == 0.9
            assert out.b == 11
        elif i== 8:
            assert out.a == 0.9
            assert out.b == 12

        i += 1
    assert i==9

