VariableGenerator_1 = VariableGenerator(
    Variable=(
        Struct(
            observations=Struct(
                tunnelflowrate=Float(-0.43),
                pressurecorner=Float(0.0)
            )
        )
    )
)
Workflow_2 = Workflow()
Flow123d_3 = Flow123dAction(
    Inputs=[
        Workflow_2.input()
    ],
    YAMLFile='V7_jb_par3.yaml'
)
conn_out = Connector()
conn_out.set_inputs([Flow123d_3])
conn_out.set_config(
    Convertor = Convertor(Struct(
        tunnelflowrate=Input(0).flow_result.balance.select(Predicate(Input(0)[1].region == ".tunnel")).head()[1].flux_out,
        pressurecorner=Input(0).flow_result.observe_data.head()[1].head().pressure_p1
    ))
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
            bounds=(0.0, 1e+10),
            init_value=0.0259
        )
    ],
    Observations=[
        CalibrationObservation(
            name="tunnelflowrate",
            group="tunel",
            weight=1.0
        ),
        CalibrationObservation(
            name="pressurecorner",
            group="tunel",
            weight=0.1
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
print_action = PrintDTTAction(
    Inputs=[Calibration_4],
    OutputFile="output.txt")
Pipeline_5 = Pipeline(
    ResultActions=[print_action]
)
