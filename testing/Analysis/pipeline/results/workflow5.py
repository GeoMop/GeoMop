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
Workflow_4.set_config(
    OutputAction=Flow123d_2,
    InputAction=Flow123d_2
)
Workflow_5 = Workflow(
    Inputs=[
        Workflow_4
    ]
)
Workflow_5.set_config(
    OutputAction=Flow123d_2,
    InputAction=Flow123d_2
)
Pipeline_6 = Pipeline(
    ResultActions=[Workflow_5]
)
