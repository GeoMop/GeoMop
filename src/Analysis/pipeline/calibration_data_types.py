from .data_types_tree import *
from .flow_data_types import Enum


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
            self.offset = init_value
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
                      model_value=Flost(),
                      residual=Float(),
                      sensitivity=Float())


class SingleIterationInfo():
    @staticmethod
    def create_type(parameters, observations):
        par = Struct()
        for p in parameters:
            setattr(par, p, SingleParameterOutput.create_type())
        obs = Struct()
        for o in parameters:
            setattr(par, o, SingleObservationOutput.create_type())
        return Struct(iteration=Int(),
                      residual=Float(),
                      converge_reason=Enum(["none", "converged", "failure"]),
                      parameters=par,
                      observations=obs)


class CalibrationOutputType():
    @staticmethod
    def create_type(parameters, observations):
        return Struct(optimisation=Sequence(SingleIterationInfo(parameters, observations)),
                      result=Struct(n_iter=Int(),
                                    converge_reason=Enum(["Free", "Tied", "Fixed", "Frozen"]),
                                    residual=Float()))
