from pipeline.data_types_tree import *

def test_struc():
    var1 = Struct(test1=Int(1), test2=String("Test"))
    var2 = Struct(test1=Int(), test2=String(), test3=Int())
    
    assert var1._is_set()
    assert var1._match_type(var2)  
    assert not var2._is_set()
    assert not var2._match_type(var1)
    
    var1 = Struct(test1=Int(1), test2=String("Test"), tests=Struct(iner1=Int(5)))
    var2 = Struct(test1=Int(), test2=String(), tests=Struct(iner1=Int(),iner2=Int()))    
    
    assert var1._is_set()
    assert not var1._match_type(var2)  
    assert not var2._is_set()
    assert var2._match_type(var1)

    var2.test1=5
    var2.test2="ooo"
    test = var2.test1
    assert test == 5
    assert var2.test1.value == 5
    assert var2.test2.value == "ooo"    
    assert var2._match_type(var1)
    var2.test1= var1.test1
    assert var2.test1.value == 1
    
    var3 = var2.duplicate()
    var3.test1 = 5
    assert var2.test1.value == 1
    assert var3.test1.value == 5
    assert var2.test2.value == var3.test2.value
    

def test_ensemble():    
    var1 = Struct(test1=Int(1), test2=String("Test"))
    var2 = Struct(test1=Int(), test2=String(), test3=Int())
    try:
        ens1 = Ensemble(var1, 
            Struct(test1=Int(1), test2=String("Test1")), 
            Struct(test1=Int(2), test2=String("Test2")), 
            Struct(test1=String('Bad type'), test2=String("Test3"))) 
        assert False, "Raise type exception fail"
    except Exception as err:
        assert str(err)[:27]=='Not supported ensemble type'
        
    try:
        ens1 = Ensemble(var1, 
            Struct(test1=Int(1), test2=String("Test1")), 
            Struct(test1=Int(2), test2=String("Test2")), 
            8)
        assert False, "Raise DTT exception fail"
    except Exception as err:
        assert str(err)=='Ensemble must have DTT value type.'

    ens1 = Ensemble(var1, 
        Struct(test1=Int(1), test2=String("Test1")), 
        Struct(test1=Int(2), test2=String("Test2")), 
        Struct(test1=Int(3), test2=String("Test3"))) 
    ens2 = Ensemble(var2, 
        Struct(test1=Int(1), test2=String("Test1"), test3=Int()), 
        Struct(test1=Int(2), test2=String("Test2"), test3=Int()), 
        Struct(test1=Int(3), test2=String("Test3"), test3=Int())) 
        
    assert ens1._is_set()
    assert ens1._match_type(ens2)  
    assert not ens2._is_set()
    assert not ens2._match_type(ens1)


def test_sequence():
    # head(), tail()
    seq = Sequence(Int(), Int(1), Int(2), Int(3), Int(4))

    assert seq.head().value == 1
    assert seq.tail().value == 4


def test_tuple():
    # _match_type(), _is_set()
    var1 = Tuple(Int(1), String("Test"))
    var2 = Tuple(Int(), String(), Int())
    var3 = Tuple(Int(), String())

    assert var1._is_set()
    assert var1._match_type(var3)
    assert not var2._is_set()
    assert not var2._match_type(var1)
    assert not var1._match_type(var2)

    # _match_type(), _is_set() with inner elements
    var1 = Tuple(Int(1), String("Test"), Tuple(Int(5)))
    var2 = Tuple(Int(), String(), Tuple(Int(), Int()))
    var3 = Tuple(Int(), String(), Tuple(Int()))

    assert var1._is_set()
    assert var1._match_type(var3)
    assert not var2._is_set()
    assert not var2._match_type(var1)
    assert not var1._match_type(var2)

    # assign, retrieve value
    var3[0].value = 5
    var3[1].value = "ooo"
    test = var3[0]
    assert test == 5
    assert var3[0].value == 5
    assert var3[1].value == "ooo"
    assert var3._match_type(var1)
    var3[0].value = var1[0]
    assert var3[0].value == 1

    # duplicate()
    var4 = var3.duplicate()
    var4[0].value = 5
    assert var3[0].value == 1
    assert var4[0].value == 5
    assert var3[1].value == var4[1].value
