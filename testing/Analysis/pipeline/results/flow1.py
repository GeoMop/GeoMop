Flow123d_1 = Flow123dAction(
    Inputs = [
        (
            Struct(
                test1=String('test')
            )
        )
    ],
    Outputs = [ 
        String('File')
    ],
    YAMLFile='test.yaml'
)
