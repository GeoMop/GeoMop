RangeGenerator_1 = RangeGenerator(
    Items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0, 'exponential':True}
    ]
)
Workflow_2 = Workflow()
Flow123d_3 = Flow123dAction(
    Inputs=[
        Workflow_2.input()
    ],
    YAMLFile='test.yaml'
)
Workflow_2.set_config(
    OutputAction=Flow123d_3,
    InputAction=Flow123d_3
)
ForEach_4 = ForEach(
    Inputs=[
        RangeGenerator_1
    ],
    WrapperActions=Workflow_2
)
Pipeline_5 = Pipeline(
    ResultActions=[ForEach_4]
)
