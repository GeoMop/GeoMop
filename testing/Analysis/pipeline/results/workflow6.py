RangeGenerator_1 = RangeGenerator(
    Items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0, 'exponential':True}
    ]
)
Workflow_3 = Workflow()
RangeGenerator_2 = RangeGenerator(
    Items = [
        {'name':'x', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'y', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0, 'exponential':True}
    ]
)
Workflow_4 = Workflow()
Flow123d_5 = Flow123dAction(
    Inputs=[
        Workflow_4.input()
    ],
    YAMLFile='pipeline/resources/test1.yaml'
)
Workflow_4.set_config(
    OutputAction=Flow123d_5,
    InputAction=Flow123d_5
)
ForEach_6 = ForEach(
    Inputs=[
        RangeGenerator_2
    ],
    WrappedAction=Workflow_4
)
Workflow_3.set_config(
    OutputAction=ForEach_6,
    InputAction=ForEach_6
)
ForEach_7 = ForEach(
    Inputs=[
        RangeGenerator_1
    ],
    WrappedAction=Workflow_3
)
Pipeline_8 = Pipeline(
    ResultActions=[ForEach_7]
)
