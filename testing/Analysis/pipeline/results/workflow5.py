VariableGenerator_3 = VariableGenerator(
    Variable=(
        Struct(
            a=String('test'),
            b=Int(3)
        )
    )
)
Workflow_4 = Workflow(
    Inputs=[
        VariableGenerator_3
    ]
)
Flow123d_5 = Flow123dAction(
    Inputs=[
        Workflow_4.input()
    ],
    YAMLFile='test.yaml'
)
Workflow_4.set_config(
    OutputAction=Flow123d_5,
    InputAction=Flow123d_5
)
Workflow_6 = Workflow(
    Inputs=[
        Workflow_4
    ]
)
Flow123d_7 = Flow123dAction(
    Inputs=[
        Workflow_6.input()
    ],
    YAMLFile='test.yaml'
)
Workflow_6.set_config(
    OutputAction=Flow123d_7,
    InputAction=Flow123d_7
)
Pipeline_8 = Pipeline(
    ResultActions=[Workflow_6]
)
