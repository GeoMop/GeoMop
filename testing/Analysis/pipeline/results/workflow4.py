Workflow_3 = Workflow(
    Inputs=[
        VariableGenerator_2
    ]
)
VariableGenerator_1 = VariableGenerator(
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
    YAMLFile='test.yaml'
)
Flow123d_5 = Flow123dAction(
    Inputs=[
        VariableGenerator_1
    ],
    YAMLFile='test2.yaml'
)
Workflow_3.set_config(
    OutputAction=Flow123d_4,
    InputAction=Flow123d_4,
    ResultActions=[Flow123d_5]
)
