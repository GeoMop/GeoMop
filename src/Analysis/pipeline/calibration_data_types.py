from .data_types_tree import *
from .flow_data_types import Enum

from enum import IntEnum
import numpy as np


class CalibrationParameter():
    def __init__(self, name, group="", bounds=(0.0, 1.0), init_value=None, offset=None, scale=1.0,
                 fixed=False, log_transform=False, tied=None):
        """
        :param string name: parameter name, in configuration and inside model
        :param string group: parameter group
        :param (float, float) bounds: lower and upper parameter bounds
        :param float init_value: initial value of parameter
        :param float offset:
        :param float scale:
        :param bool fixed: if True then parameter is fixed in init value
        :param bool log_transform: if True the body parameter is scale * exp( tuned parameter ) + offset
        :param string tied: python expression, may use other parameters, this parameter is not calibrated
        """

        self.name = name
        self.group = group
        self.bounds = bounds

        if init_value is None:
            self.init_value = (bounds[0] + bounds[1]) / 2
        else:
            self.init_value = init_value

        if offset is None:
            self.offset = 0.0
        else:
            self.offset = offset

        self.scale = scale
        self.fixed = fixed
        self.log_transform = log_transform
        self.tied = tied


class CalibrationObservationType(IntEnum):
    """Calibration Observation Type"""
    scalar = 0
    time_series = 1


class CalibrationObservation():
    def __init__(self, name, group="", observation_type=CalibrationObservationType.scalar, weight=1.0):
        """
        :param string name: observation name
        :param string group: observation group
        :param CalibrationObservationType observation_type: observation type
        :param float weight: observation weight in target function
        """

        self.name = name
        self.group = group
        self.observation_type = observation_type
        self.weight = weight


class CalibrationAlgorithmParameter():
    def __init__(self, group="", diff_inc_rel=0.01, diff_inc_abs=0.01):
        """
        :param string group: parameter group
        :param float diff_inc_rel: step for derivation eval relative
        :param float diff_inc_abs: step for derivation eval absolute
        """

        self.group = group
        self.diff_inc_rel = diff_inc_rel
        self.diff_inc_abs = diff_inc_abs


class CalibrationTerminationCriteria():
    def __init__(self, n_lowest=10, tol_lowest=1e-6, n_from_lowest=10,
                 n_param_change=10, tol_rel_param_change=1e-6, n_max_steps=100):
        """
        :param int n_lowest:
        :param float tol_lowest: stop if difference of min and max
            from n_lowest min values of objective function
        :param int n_from_lowest: stop if n iterations without improvement
        :param int n_param_change:
        :param float tol_rel_param_change: stop if max relative change of parameter form last n_param_change
            is lower than tol_rel_param_change (must be satisfied for all parameters)
        :param int n_max_steps: maximum number of iterations to perform
        """

        self.n_lowest = n_lowest
        self.tol_lowest = tol_lowest
        self.n_from_lowest = n_from_lowest
        self.n_param_change = n_param_change
        self.tol_rel_param_change = tol_rel_param_change
        self.n_max_steps = n_max_steps

    # ToDo:
    def get_terminator(self):
        n_iterations = [0]
        lowest_list = []
        lowest_f = [0]
        lowest_i = [0]
        last_x = [None]

        def terminator(x, f, g):
            ret = False

            n_iterations[0] += 1

            # n_lowest, tol_lowest
            # if len(lowest_list) < self.n_lowest:
            #     lowest_list.append(f)
            # else:
            #     for v in lowest_list

            # n_from_lowest
            if n_iterations[0] == 1:
                lowest_f[0] = f
            if f < lowest_f[0]:
                lowest_f[0] = f
                lowest_i[0] = n_iterations[0]
            if n_iterations[0] - lowest_i[0] >= self.n_lowest:
                ret = True

            # n_param_change, tol_rel_param_change

            # n_max_steps
            if n_iterations[0] >= self.n_max_steps:
                ret = True

            # internal termination criteria
            eps = 1e-8
            if f < eps:
                ret = True
            if np.linalg.norm(g) < eps:
                ret = True
            if last_x[0] is not None and np.linalg.norm(x - last_x[0]) < eps:
                ret = True

            last_x[0] = x

            return ret

        return terminator


class SingleParameterOutput():
    @staticmethod
    def create_type():
        return Struct(parameter_type=Enum(["Free", "Tied", "Fixed", "Frozen"]),
                      value=Float(),
                      interval_estimate=Tuple(Float(), Float()),
                      sensitivity=Float(),
                      relative_sensitivity=Float())


class SingleObservationOutput():
    @staticmethod
    def create_type():
        return Struct(measured_value=Float(),
                      model_value=Float(),
                      residual=Float(),
                      sensitivity=Float())


class SingleIterationInfo():
    @staticmethod
    def create_type(parameters, observations):
        par = Struct()
        for p in parameters:
            setattr(par, p.name, SingleParameterOutput.create_type())
        obs = Struct()
        for o in observations:
            setattr(par, o.name, SingleObservationOutput.create_type())
        return Struct(iteration=Int(),
                      residual=Float(),
                      converge_reason=Enum(["none", "converged", "failure"]),
                      parameters=par,
                      observations=obs)


class CalibrationOutputType():
    @staticmethod
    def create_type(parameters, observations):
        return Struct(optimisation=Sequence(SingleIterationInfo.create_type(parameters, observations)),
                      result=Struct(n_iter=Int(),
                                    converge_reason=Enum(["none", "converged", "failure"]),
                                    residual=Float()))
