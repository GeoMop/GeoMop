VariableGenerator_1 = VariableGenerator(
    Variable=(
        Struct(
            test1=String('test')
        )
    )
)
Flow123d_2 = Flow123dAction(
    Inputs=[
        VariableGenerator_1
    ],
    YAMLFile='test.yaml'
)
