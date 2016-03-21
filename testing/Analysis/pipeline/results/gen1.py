RangeGenerator_1 = RangeGenerator(
    Outputs = [
        (
            Ensemble(
                (
                    Struct(
                        a=Int(1),
                        b=Int(10)
                    )
                )
            )
        )
    ],
    Items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':3, 'exponential':True}
    ]
)
