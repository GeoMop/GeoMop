from Analysis.pipeline.parametrized_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.wrapper_actions import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.workflow_actions import *
from Analysis.pipeline.pipeline import *
from Analysis.pipeline.pipeline_processor import *
import Analysis.pipeline.action_types as action
from .pomfce import *
import shutil


def test_calibration_termination_criteria():
    def xfg(x, f, g):
        return np.array(x, np.float64), f, np.array(g, np.float64)

    def tt(t, m):
        for i in range(len(m)):
            if t(*xfg(*m[i])):
                return i
        return -1

    crit = CalibrationTerminationCriteria(n_lowest=3, tol_lowest=1e-2, n_from_lowest=3,
                 n_param_change=3, tol_rel_param_change=1e-2, n_max_steps=10)

    ts = [
        ([1.0, 2.0], 1.0, [0.1, 0.2]),
        ([1.1, 2.1], 0.9, [0.1, 0.2]),
        ([1.2, 2.2], 0.8, [0.1, 0.2]),
        ([1.3, 2.3], 0.7, [0.1, 0.2]),
        ([1.4, 2.4], 0.6, [0.1, 0.2]),
        ([1.5, 2.5], 0.5, [0.1, 0.2]),
        ([1.6, 2.6], 0.4, [0.1, 0.2]),
        ([1.7, 2.7], 0.3, [0.1, 0.2]),
        ([1.8, 2.8], 0.2, [0.1, 0.2]),
        ([1.9, 2.9], 0.1, [0.1, 0.2])
    ]

    # n_lowest, tol_lowest
    t = crit.get_terminator()
    m = ts.copy()
    m[2] = ([1.2, 2.2], 0.899, [0.1, 0.2])
    m[3] = ([1.3, 2.3], 0.898, [0.1, 0.2])
    assert tt(t, m) == 3

    # n_from_lowest
    t = crit.get_terminator()
    m = ts.copy()
    m[1] = ([1.1, 2.1], 0.1, [0.1, 0.2])
    assert not t(*xfg(*m[0]))
    assert not t(*xfg(*m[1]))
    assert not t(*xfg(*m[2]))
    assert not t(*xfg(*m[3]))
    assert t(*xfg(*m[4]))

    # n_param_change, tol_rel_param_change
    t = crit.get_terminator()
    m = ts.copy()
    m[2] = ([1.1001, 2.2], 0.8, [0.1, 0.2])
    m[3] = ([1.1002, 2.2001], 0.7, [0.1, 0.2])
    m[4] = ([1.1003, 2.2002], 0.6, [0.1, 0.2])
    m[5] = ([1.1004, 2.2003], 0.5, [0.1, 0.2])
    assert tt(t, m) == 5

    # n_max_steps
    t = crit.get_terminator()
    m = ts.copy()
    assert tt(t, m) == 9

    # internal termination criteria
    # f == 0
    t = crit.get_terminator()
    m = ts.copy()
    m[3] = ([1.3, 2.3], 0.0, [0.1, 0.2])
    assert tt(t, m) == 3

    # g == 0
    t = crit.get_terminator()
    m = ts.copy()
    m[3] = ([1.3, 2.3], 0.7, [0.0, 0.0])
    assert tt(t, m) == 3

    # last_x - x == 0
    t = crit.get_terminator()
    m = ts.copy()
    m[3] = ([1.2, 2.2], 0.7, [0.1, 0.2])
    assert tt(t, m) == 3


def test_calibration(request):
    def clear_backup():
        shutil.rmtree("backup", ignore_errors=True)
    request.addfinalizer(clear_backup)

    action.__action_counter__ = 0
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
                group="pokus",
                bounds=(-1e+10, 1e+10),
                init_value=1.0
            ),
            CalibrationParameter(
                name="x2",
                group="pokus",
                bounds=(-1e+10, 1e+10),
                init_value=1.0
            )
        ],
        Observations=[
            CalibrationObservation(
                name="y1",
                group="tunel",
                weight=1.0
            ),
            CalibrationObservation(
                name="y2",
                group="tunel",
                weight=1.0
            )
        ],
        AlgorithmParameters=[
            CalibrationAlgorithmParameter(
                group="pokus",
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
    p = Pipeline(
        ResultActions=[cal]
    )

    pp = Pipelineprocessor(p)
    err = pp.validate()
    assert len(err) == 0

    # _get_settings_script
    test = cal._get_settings_script()
    compare_with_file("cal1.py", test)

    # run pipeline
    pp.run()
    i = 0

    while pp.is_run():
        time.sleep(0.1)

        i += 1
        assert i < 1000, "Timeout"

    # test residual
    assert cal._output.result.residual.value < 0.01
