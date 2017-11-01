Analysis - Calibration
======================

Configuration
-------------

WrappedAction
    Workflow of calibrated model

Parameters
    List of parameters

    name
        Name of parameter in calibration and inside of model

    group
        Group of parameter

    bounds
        Upper and lower bound of parameter

    init_value
        Init value of parameter

    offset, scale
        Body param. = scale * tuned param. + offset; default offset = 0.0, scale = 1.0

    fixed
        If True then parameter is fixed in init value

    log_transform
        If True with parameter is internally operated as log10(parameter value)

    tied_params
        Parameters used in tied_expression

    tied_expression
        Python expression, may use other parameters (defined in tied_params),
        this parameter is not calibrated

Observations
    List of observations

    name
        Name of observation

    group
        Group of observation

    weight
        Observation weight in target function

    upper_bound:
        If computed value is greater than this parameter, special penalization is applied

    lower_bound:
        If computed value is smaller than this parameter, special penalization is applied

AlgorithmParameters
    Define approximation of derivatives, for each group of parameters.

    group:
        Parameter group

    diff_inc_rel
        Step for derivation eval relative

    diff_inc_abs
        Step for derivation eval absolute

TerminationCriteria
    Define criteria for termination of calibration process.

    n_lowest, tol_lowest
        Stop if difference of min and max from n_lowest min values of objective function

    n_from_lowest
        Stop if n iterations without improvement

    n_param_change, tol_rel_param_change
        Stop if max relative change of parameter form last n_param_change is lower than tol_rel_param_change
        (must be satisfied for all parameters)

    n_max_steps
        Maximum number of iterations to perform

MinimizationMethod
    Sets minimalization method. Must be one of:

        - L-BFGS-B - Limited-memory Broyden–Fletcher–Goldfarb–Shanno with bounds
        - SLSQP - Sequential Least SQuares Programming

BoundsType
    Sets type of bounds of parameters. Must be one of:

        - hard - use bounds from underlying SciPy minimize
        - soft - use penalization if parameter go out of bounds

Calibration input
-----------------

observations
    Struct of individual observations

Calibration output
------------------

optimisation
    Sequence of individual iterations:

    converge_reason
        Reason of convergence

    cumulative_n_evaluation
        Number of evaluation of criterial functon

    residual
        Criterial function in this iteration

    observations
        measured_value
            Desired value

        model_value
            Observation value corresponding to input parameters

        residual
            Difference between measured_value and model_value

        sensitivity
            Sensitivity of observation j is the magnitude of the j’th row of the
            Jacobian multiplied by the weight associated with that observation; this magnitude is then
            divided by the number of adjustable parameters. It is thus a measure of the sensitivity of that
            observation to all parameters involved in the parameter estimation process.

    parameters
        parameter_type
            Type of parameter, is one of Free, Tied, Fixed, Frozen

        value
            Parameter value in this iteration

        interval_estimate
            Not implemented yet

        sensitivity
            Sensitivity of the i’th parameter is the normalised (with respect to the number of observations)
            magnitude of the column of the Jacobian matrix pertaining to that parameter, with each
            element of that column multiplied by the weight pertaining to the respective observation.

        relative_sensitivity
            The relative sensitivity of a parameter is obtained by multiplying its
            sensitivity by the magnitude of the value of the parameter. It is thus a measure of the
            changes in model outputs that are incurred by a fractional change in the value of
            the parameter.

result
    n_iter
        Number of iterations

    converge_reason
        Reason of convergence

    residual
        Criterial function after calibration
