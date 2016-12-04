VariableGenerator_1 = VariableGenerator(
    Variable=(
        Struct(
            observations=Struct(tunnelflowrate=Float(-1.05))
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
conn_out = Connector()
conn_out.set_inputs([Flow123d_3])
conn_out.set_config(
    Convertor = Convertor(Struct(tunnelflowrate=Input(0).flow_result.balance.select(
        Predicate(Input(0)[1].region == ".tunnel")).head()[1].flux_out))
)
Workflow_2.set_config(
    OutputAction=conn_out,
    InputAction=Flow123d_3
)
Calibration_4 = Calibration(
    Inputs=[
        VariableGenerator_1
    ],
    WrappedAction=Workflow_2,
    Parameters=[
        CalibrationParameter(
            name="vodivost",
            group="pokus",
            bounds=(-1e+10, 1e+10),
            init_value=0.0259
        )
    ],
    Observations=[
        CalibrationObservation(
            name="tunnelflowrate",
            group="tunel"
        )
    ],
    AlgorithmParameters=[
        CalibrationAlgorithmParameter(
            group="pokus",
            diff_inc_rel=0.0,
            diff_inc_abs=0.0001
        )
    ],
    TerminationCriteria=CalibrationTerminationCriteria(
        n_max_steps=100
    ),
    MinimizationMethod="SLSQP"
)
Pipeline_5 = Pipeline(
    ResultActions=[Calibration_4]
)
