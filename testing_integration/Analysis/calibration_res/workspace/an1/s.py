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
conn = Connector()
conn.set_inputs([Flow123d_3])
conn.set_config(
    Convertor = Convertor(Struct(tunnelflowrate=Input(0).flow_result.balance.select(Predicate(Input(0)[1].region == ".tunnel")).head()[1].flux_out))
)
Workflow_2.set_config(
    OutputAction=conn,
    InputAction=Flow123d_3
)
Calibration_4 = Calibration(
    Inputs=[
        VariableGenerator_1
    ],
    WrappedAction=Workflow_2,
    Parameters=[
        CalibrationParameter(
            name="cond",
            group="pokus",
            bounds=(-1e+10, 1e+10),
            init_value=0.0259
        )
    ],
    Observations=[
        CalibrationObservation(
            name="tunnelflowrate",
            observation=-1.05,
            group="tunel"
        )
    ],
    TerminationCriteria=CalibrationTerminationCriteria(
        n_max_steps=100
    )
)
Pipeline_5 = Pipeline(
    ResultActions=[Calibration_4]
)
