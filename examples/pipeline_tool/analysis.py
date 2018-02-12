gen = VariableGenerator(
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
workflow = Workflow()
flow = Flow123dAction(
    Inputs=[
        workflow.input()
    ],
    YAMLFile='V7_jb_par.yaml'
)
workflow.set_config(
    OutputAction=flow,
    InputAction=flow
)
foreach = ForEach(
    Inputs=[
        gen
    ],
    WrappedAction=workflow
)
pipeline = Pipeline(
    ResultActions=[foreach]
)
