RangeGenerator_1 = RangeGenerator(
    Outputs = [
        (
            Ensemble(
                (
                    Struct(
                        a=Float(None),
                        b=Float(None)
                    )
                )
            )
        )
    ],
    Items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0, 'exponential':True}
    ]
)
ForEach_2 = ForEach(
    Inputs = [
        RangeGenerator_1
    ]
)
Flow123d_3 = Flow123dAction(
    Inputs = [
        ForEach_2
    ],
    Outputs = [
        String('File')
    ],
    YAMLFile='test.yaml'
)
ForEach_2.set_wrapped_action(Flow123d_3)
Workflow_4 = Workflow(
    InputAction=RangeGenerator_1,
    OutputAction=ForEach_2
)
