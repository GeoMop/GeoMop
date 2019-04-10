RangeGenerator_1 = RangeGenerator(
    Items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0, 'exponential':True}
    ]
)
Workflow_3 = Workflow()
VariableGenerator_2 = VariableGenerator(
    Variable=(
        Struct(
            a=String('test'),
            b=Int(3)
        )
    )
)
Flow123d_4 = Flow123dAction(
    Inputs=[
        Workflow_3.input()
    ],
    YAMLFile='resources/test1.yaml'
)
Flow123d_5 = Flow123dAction(
    Inputs=[
        VariableGenerator_2
    ],
    YAMLFile='resources/test2.yaml'
)
Workflow_3.set_config(
    OutputAction=Flow123d_4,
    InputAction=Flow123d_4,
    ResultActions=[Flow123d_5]
)
ForEach_6 = ForEach(
    Inputs=[
        RangeGenerator_1
    ],
    WrappedAction=Workflow_3
)
Pipeline_7 = Pipeline(
    ResultActions=[ForEach_6]
)
