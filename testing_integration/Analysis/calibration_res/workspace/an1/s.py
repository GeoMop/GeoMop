VariableGenerator_1 = VariableGenerator(
    Variable=(
        Struct(
            observations=Struct(tunnelflowrate=Float(-1.05))
        )
    )
)
Workflow_2 = Workflow()
conn_in = Connector()
conn_in.set_inputs([Workflow_2.input()])
conn_in.set_config(
    Convertor = Convertor(Input(0).parameters)
)
Flow123d_3 = Flow123dAction(
    Inputs=[
        conn_in
    ],
    YAMLFile='V7_jb_par.yaml'
)
conn_out = Connector()
conn_out.set_inputs([Flow123d_3])
conn_out.set_config(
    Convertor = Convertor(Struct(tunnelflowrate=Input(0).flow_result.balance.select(Predicate(Input(0)[1].region == ".tunnel")).head()[1].flux_out))
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
            name="cond",
            group="pokus",
            bounds=(-1e+10, 1e+10),
            init_value=0.0259
        )
    ],
    Observations=[
        CalibrationObservation(
            name="tunnelflowrate",
            #observation=-1.05,
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
    )
)
Pipeline_5 = Pipeline(
    ResultActions=[Calibration_4]
)
