import pipeline as p

def test_classes():
    try:
        p.Int()
        p.Bool()
        p.Float()
        p.String()
        p.Struct()
        p.Ensemble(p.Int())
        p.And(p.Bool(True), p.Bool(False))
        p.Or(p.Bool(True), p.Bool(False))
        p.Input()
        p.CommonConvertor()
        p.RangeGenerator()
        p.VariableGenerator()
        p.Flow123dAction()
        p.Predicate()
        p.Pipeline()
        p.Workflow()
        p.ForEach()
    except:
        assert False, "All public classes are not vissible"
    
    for types in (
        "DTT", "BaseDTT", " CompositeDTT", "CompositiIter", "SortableDTT",
        "PredicatePoint", "TT", "GDTT_Operators", "GDTT",  " GDTTFunc"
    ):
        try:
            test = eval("p."+types+"()")
        except:
            continue
        assert test is None , "Private module class {0} is vissible".format(types)
