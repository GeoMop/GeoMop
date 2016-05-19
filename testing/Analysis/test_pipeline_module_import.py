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
        p.Connector()
        p.RangeGenerator()
        p.VariableGenerator()
        p.Flow123dAction()
        p.Convertor(p.Input(0))
        p.Predicate(p.Input(0))
        p.KeyConvertor(p.Input(0))
        p.Adapter(p.Input(0))
        p.Pipeline()
        p.Workflow()
        p.ForEach()
    except:
        assert False, "All public classes are not vissible"
    
    for types in (
        "DTT", "BaseDTT", " CompositeDTT", "CompositiIter", "SortableDTT",
        "PredicatePoint", "TT", "GDTT",  "GDTTFunc", 
        "Bridge", " ActionType", "ActionStateType", "BaseActionType", 
        "ConnectorActionType", "  GeneratorActionType", "ParametrizedActionType", 
        "WrapperActionType", "WorkflowActionType"
    ):
        try:
            test = eval("p."+types+"()")
        except:
            continue
        assert test is None , "Private module class {0} is vissible".format(types)
