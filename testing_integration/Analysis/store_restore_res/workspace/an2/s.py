VariableGenerator_1 = VariableGenerator(
    Variable=(
        Ensemble(
            (
                Struct(
                    cond=Float()
                )
            ),
            (
                Struct(
                    cond=Float(0.06)
                )
            ),
            (
                Struct(
                    cond=Float(0.07)
                )
            ),
            (
                Struct(
                    cond=Float(0.08)
                )
            )
        )
    )
)
Workflow_2 = Workflow()
Flow123d_3 = Flow123dAction(
    Inputs=[
        Workflow_2.input()
    ],
    YAMLFile='V7_jb_par.yaml'
)
VariableGenerator_4 = VariableGenerator(
    Variable=(
        Struct(
            cond=Float(0.09)
        )
    )
)
Flow123d_5 = Flow123dAction(
    Inputs=[
        VariableGenerator_4
    ],
    YAMLFile='V7_jb_par.yaml'
)
Workflow_2.set_config(
    OutputAction=Flow123d_3,
    InputAction=Flow123d_3,
    ResultActions=[Flow123d_5]
)
ForEach_6 = ForEach(
    Inputs=[
        VariableGenerator_1
    ],
    WrappedAction=Workflow_2
)
Pipeline_7 = Pipeline(
    ResultActions=[ForEach_6]
)
