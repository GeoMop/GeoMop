RangeGenerator_1 = RangeGenerator(
    Output=(
        Ensemble(
            (
                Struct(
                    a=Float(),
                    b=Float()
                )
            )
        )
    ),
    Items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':0, 'exponential':True}
    ]
)
Workflow_2 = Workflow()
Flow123d_3 = Flow123dAction(
    Input=Workflow_2.input(),
    Output=String('File'),
    YAMLFile='test.yaml'
)
Workflow_2.set_output_action(Flow123d_3)
Workflow_2.set_input_action(Flow123d_3)
ForEach_4 = ForEach(
    Input=RangeGenerator_1
)
Pipeline_5 = Pipeline(
    OutputActions=[ForEach_4]
)
