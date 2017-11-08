Analysis - Actions
==================

One action is a specific computational or graphic operation.
The specific details of the performed operations can be affected by the action configuration.
Each action has either one Input Slot and one Output Slot.
The input and output data type is fixed by the action type and its configuration.
Action configuration can affect the data type of input and output slots.
The configuration can not be the result of another action, its specification is part of the workflow definition.

Generator actions
-----------------

VariableGenerator
~~~~~~~~~~~~~~~~~

The data passed in the configuration, provides on the output.

An example::

    var = Struct(x1=Float(1.0), x2=Float(2.0))
    gen = VariableGenerator(Variable=var)

RangeGenerator
~~~~~~~~~~~~~~

Generator for generation parallel lists.

An example::

    items = [
        {'name':'a', 'value':1, 'step':0.1, 'n_plus':1, 'n_minus':1,'exponential':False},
        {'name':'b', 'value':10, 'step':1, 'n_plus':2, 'n_minus':3,'exponential':False}
    ]
    gen = RangeGenerator(Items=items, AllCases=False)

Output of action "gen" is::

    Ensemble(
        Struct(a=Float(1.0), b=Float(10.0)),
        Struct(a=Float(1.1), b=Float(10.0)),
        Struct(a=Float(0.9), b=Float(10.0)),
        Struct(a=Float(1.0), b=Float(11.0)),
        Struct(a=Float(1.0), b=Float(12.0)),
        Struct(a=Float(1.0), b=Float(9.0)),
        Struct(a=Float(1.0), b=Float(8.0)),
        Struct(a=Float(1.0), b=Float(7.0))
    )

Parametrized actions
--------------------

The common denominator of these actions is that they call non-trivial external programs and
assume the definition of the data of these programs in specific contexts,
the input of actions can only affect the declared parameters in the input data (files) of each program.

Flow123dAction
~~~~~~~~~~~~~~
Action implements Flow123d simulation.
Configuration includes a YAML file and a given computing network.

An example::

    gen = VariableGenerator(Variable=Struct(par=Float(1.2)))
    flow = Flow123dAction(Inputs=[gen], YAMLFile="test.yaml")

FunctionAction
~~~~~~~~~~~~~~

This action compute some mathematical expressions on input data and return results on output.

An example::

    var = Struct(x1=Float(1.0), x2=Float(2.0), x3=Float(math.pi/2))
    gen = VariableGenerator(Variable=var)
    fun = FunctionAction(
        Inputs=[gen],
        Params=["x1", "x2", "x3"],
        Expressions=["y1 = 2 * x1 + 3 * x2", "y2 = sin(x3)"])

Output of action "fun" is::

    Struct(y1=Float(8.0), y2=Float(1.0))

Wrapper actions
---------------

ForEach
~~~~~~~

The action configuration includes a workflow with IN input type and OUT output type.
The workflow is executed on all input elements of type Ensemble(IN), resulting in output of type Ensemble(OUT).

An example::

    var = Ensemble(Float(), Float(1.0), Float(2.0), Float(3.0))
    gen = VariableGenerator(Variable=var)
    w = Workflow()
    f = FunctionAction(
        Inputs=[w.input()],
        Params=["x"],
        Expressions=["y = 2 * x"]
    )
    w.set_config(
        OutputAction=f,
        InputAction=f
    )
    for_each = ForEach(
        Inputs=[gen],
        WrappedAction=w
    )

Calibration
~~~~~~~~~~~

Calibrating a generic model for given data, ie identifying model parameters so that
the result of the model was in some sense the closest measured data.

An example::

    gen = VariableGenerator(
        Variable=(
            Struct(
                observations=Struct(
                    y1=Float(1.0),
                    y2=Float(5.0)
                )
            )
        )
    )
    w = Workflow()
    f = FunctionAction(
        Inputs=[
            w.input()
        ],
        Params=["x1", "x2"],
        Expressions=["y1 = 2 * x1 + 2", "y2 = 2 * x2 + 3"]
    )
    w.set_config(
        OutputAction=f,
        InputAction=f
    )
    cal = Calibration(
        Inputs=[
            gen
        ],
        WrappedAction=w,
        Parameters=[
            CalibrationParameter(
                name="x1",
                group="test",
                bounds=(-1e+10, 1e+10),
                init_value=1.0
            ),
            CalibrationParameter(
                name="x2",
                group="test",
                bounds=(-1e+10, 1e+10),
                init_value=1.0
            )
        ],
        Observations=[
            CalibrationObservation(
                name="y1",
                group="tunnel",
                weight=1.0
            ),
            CalibrationObservation(
                name="y2",
                group="tunnel",
                weight=1.0
            )
        ],
        AlgorithmParameters=[
            CalibrationAlgorithmParameter(
                group="test",
                diff_inc_rel=0.01,
                diff_inc_abs=0.0
            )
        ],
        TerminationCriteria=CalibrationTerminationCriteria(
            n_max_steps=100
        ),
        MinimizationMethod="SLSQP",
        BoundsType=CalibrationBoundsType.hard
    )

Output actions
--------------

PrintDTTAction
~~~~~~~~~~~~~~

Saves input data to file.

An example::

    print_action = PrintDTTAction(
        Inputs=[some_action],
        OutputFile="output.txt")

Special actions
---------------

Workflow
~~~~~~~~

Encapsulates the entire workflow into a new user-defined action.

An example::

    w = Workflow()
    f = FunctionAction(
        Inputs=[w.input()],
        Params=["x1", "x2"],
        Expressions=["y1 = 2 * x1 + 2", "y2 = 2 * x2 + 3"]
    )
    w.set_config(
        OutputAction=f,
        InputAction=f
    )

Pipeline
~~~~~~~~

Pipeline groups all of other actions.
It has not any input action and least one output action.
Output action define action contained in pipeline.
Output action would be actions, theirs results will be downloaded.

An example::

    var = Struct(x1=Float(1.0), x2=Float(2.0))
    gen = VariableGenerator(Variable=var)
    print_action = PrintDTTAction(
        Inputs=[gen],
        OutputFile="output.txt")
    pipeline = Pipeline(
        ResultActions=[print_action]
    )

Connector
~~~~~~~~~

Connectors are used for modification of data between individual actions.

An example::

    var = Struct(x1=Float(1.0), x2=Float(2.0))
    gen = VariableGenerator(Variable=var)

    # convert data from Struct(x1=Float(), x2=Float()) to Struct(a=Float(), b=Float())
    conn = Connector()
    conn.set_inputs([gen])
    conn.set_config(
        Convertor=Convertor(Struct(a=Input(0).x1, b=Input(0).x2))
    )

    print_action = PrintDTTAction(
        Inputs=[gen],
        OutputFile="output.txt")
