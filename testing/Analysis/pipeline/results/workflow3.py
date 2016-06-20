Workflow_2 = Workflow(
    Inputs=[
        VariableGenerator_1
    ]
)
Flow123d_3 = Flow123dAction(
    Inputs=[
        Workflow_2.input()
    ],
    YAMLFile='test1.yaml'
)
Flow123d_4 = Flow123dAction(
    Inputs=[
        Flow123d_3
    ],
    YAMLFile='test2.yaml'
)
Workflow_2.set_config(
    OutputAction=Flow123d_4,
    InputAction=Flow123d_3
)
