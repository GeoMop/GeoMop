Workflow_2 = Workflow(
    Inputs=[
        VariableGenerator_1
    ]
)
Flow123d_3 = Flow123dAction(
    Inputs=[
        Workflow_2.input()
    ],
    YAMLFile='resources/test1.yaml'
)
Workflow_2.set_config(
    OutputAction=Flow123d_3,
    InputAction=Flow123d_3
)
