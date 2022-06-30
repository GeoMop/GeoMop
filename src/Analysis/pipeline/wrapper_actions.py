from .action_types import WrapperActionType, ActionStateType, BaseActionType, ActionsStatistics, ActionRunningState
from .data_types_tree import Ensemble, DTT
from .generator_actions import VariableGenerator
from .workflow_actions import Workflow
from .data_types_tree import Struct, Float
from .calibration_data_types import *
#from .calibration_lbfgsb import min_lbfgsb
#from .calibration_slsqp import min_slsqp

import threading
import time
from enum import IntEnum
import math
from math import *

import numpy as np
from scipy.optimize import minimize
from scipy.optimize import differential_evolution


class ForEach(WrapperActionType):
    
    name = "ForEach"
    """Display name of action"""
    description = "Cyclic action processor"
    """Display description of action"""  

    def __init__(self, **kwargs):
        """
       Class for cyclic action processing.      
        :param BaseActionType WrappedAction: Wrapped action
        :param Ensemble Output: This variable is compute  from outputs
            WrappedAction and placed in Ensemble
        :param Action Input:  Action that return Ensemble, composite of 
            WrappedAction cyclic  inputs, this parameter is set after declaration 
            this action by function set_wrapped_action 
        """
        self._wa_instances=[]
        """
        Set wrapper class serve only as template, for run is make
        copy of this class. The variable is for the copies.
        """
        self._procesed_instances = 0
        """How many instances is procesed"""
        super(ForEach, self).__init__(**kwargs)        

    def _set_bridge(self, bridge):
        """redirect bridge to wrapper"""
        bridge._set_new_link(self, self._get_output_to_wrapper)

    def _inicialize(self):
        """inicialize action run variables"""
        super(ForEach, self)._inicialize()
        self.__make_output()

    def _get_output_to_wrapper(self):
        """return output relevant for wrapper action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            # for wraped action return previous input
            ensemble = self.get_input_val(0)
            if isinstance(ensemble,  Ensemble):
                return ensemble.subtype
        return None

    def __make_output(self):
        """return output relevant for set action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            output=self._variables['WrappedAction']._get_output()
            if not isinstance(output, DTT):    
                return None
            res=Ensemble(output)
            if not self._is_state(ActionStateType.finished):
                for instance in self._wa_instances:
                    """Running instance, get input from generator"""
                    res.add_item(instance._get_output())
            self._output = res
        
    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super(ForEach, self)._get_variables_script()        
        if 'WrappedAction' in self._variables:
            wrapper = 'WrappedAction={0}'.format(self._variables['WrappedAction']._get_instance_name())
            var.append([wrapper])
        return var
        
    def _set_storing(self, identical_list):
        """set restore id"""
        super(ForEach, self)._set_storing(identical_list)
        if 'WrappedAction' in self._variables:
            self._variables['WrappedAction']._set_storing(identical_list)

    def _plan_action(self, path):
        """
        If next action can be panned, return processed state and 
        this action, else return processed state and null        
        """
        if self._is_state(ActionStateType.processed):
            return ActionRunningState.wait,  None
        if self._is_state(ActionStateType.finished):            
            return ActionRunningState.finished,  self
        if len( self._wa_instances)==0:
            if self._restore_id is not None:
                # restoring - set processed state as in classic action                
                if self._is_state(ActionStateType.processed):
                    return ActionRunningState.wait,  None                        
                self._restore_results(path)
                if self._restore_id is not None:
                    self._set_state(ActionStateType.processed)
                    # send as short action for storing and settings state
                    return ActionRunningState.repeat,  self
            ensemble = []
            for i in range(0, len(self._inputs)):
                ensemble.append(self.get_input_val(i))
            if len(ensemble[0])== 0:
                return ActionRunningState.error,  \
                    ["Empty Ensemble in ForEach input"]
            for i in range(0, len(ensemble[0]._list)):
                inputs = []
                for j in range(0, len(self._inputs)):
                    if len(ensemble[j])<=i:
                        return ActionRunningState.error,  \
                            ["Ensamble in Input({0}) has less items".format(str(i))]
                    gen = VariableGenerator(Variable=ensemble[j]._list[i])
                    gen._inicialize()
                    gen._update()
                    gen._after_update(None)
                    if self._inputs[j]._restore_id is not None:
                        # input is restored => mark generator as restored
                        gen._set_restored()
                    inputs.append(gen) 
                name = self._variables['WrappedAction']._get_instance_name()
                script = self._variables['WrappedAction']._get_settings_script()
                script.insert(0, "from Analysis.pipeline import *")
                script = '\n'.join(script)
                script = script.replace(name, "new_dupl_workflow")
                exec (script, globals())
                self._wa_instances.append(new_dupl_workflow)
                self._wa_instances[-1].set_inputs(inputs)
                self._wa_instances[-1]._inicialize()
                self._wa_instances[-1]._reset_storing(
                    self._variables['WrappedAction'], self._index_iden +"_"+ str(i)) 
        if self._procesed_instances == len(self._wa_instances):
            for instance in self._wa_instances:
                if not instance._is_state(ActionStateType.finished):
                    return ActionRunningState.wait, None
            self._set_state(ActionStateType.processed)
            self.__make_output()
            return ActionRunningState.repeat, self
        next_wa = self._procesed_instances
        while next_wa < len(self._wa_instances):    
            state, action = self._wa_instances[next_wa]._plan_action(path)
            if state is ActionRunningState.finished:
                if next_wa == self._procesed_instances:
                    self._procesed_instances += 1
                    # Next line indented to fix bug with repeatedly running underlying workflow.
                    return ActionRunningState.wait, action
            if state is ActionRunningState.repeat:
                return state, action
            if state is ActionRunningState.error:
                return state, action
            if state is ActionRunningState.wait and action is not None:
                return ActionRunningState.repeat, action
            # run return wait, try next
            next_wa += 1            
        return  ActionRunningState.wait, None

    def _check_params(self):
        """check if all require params is set"""
        err = super(ForEach, self)._check_params()
        if len(self._inputs) == 0:
            self._add_error(err, "No input action for ForEach")
        if  'WrappedAction' in self._variables:            
            if not isinstance(self._variables['WrappedAction'],  Workflow):
                self._add_error(err, "Parameter 'WrappedAction' must be Workflow")
            
        for i in range(0, len(self._inputs)):
            ensemble = self.get_input_val(i)
            if not isinstance(ensemble,  Ensemble):
                self._add_error(err, "Input action {0} not produce Ensemble type variable".format(str(i)))
        return err
        
    def validate(self):    
        """validate variables, input and output"""
        err = super(ForEach, self).validate()
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            err.extend(self._variables['WrappedAction'].validate())
        return err
        
    def _get_statistics(self):
        """return all statistics for this and child action"""
        stat = self._variables['WrappedAction']._get_statistics()
        number = 0
        if len(self._wa_instances)>0:
            number = len(self._wa_instances)
        else:
            ensemble = self.get_input_val(0)
            number = len(ensemble)
        ret = ActionsStatistics()
        ret.add(stat, number)
        return ret


class Calibration(WrapperActionType):
    class ScipyState(IntEnum):
        created = 0
        running = 1
        finished = 3

    name = "Calibration"
    """Display name of action"""
    description = "Calibration of model parameters"
    """Display description of action"""

    def __init__(self, **kwargs):
        """
        Class for calibration of model parameters.
        :param Workflow WrappedAction: Wrapped action
        :param list of CalibrationParameter Parameters: list of parameters to calibrate
        :param list of CalibrationObservation Observations: list of observations
        :param list of CalibrationAlgorithmParameter AlgorithmParameters: list of algorithm parameters
        :param CalibrationTerminationCriteria TerminationCriteria: termination criteria
        :param str MinimizationMethod: type of solver
        :param CalibrationBoundsType BoundsType: type of bounds
        :param CalibrationOutputType Output: output from calibration
        :param Action Input: action that return input to calibration
        """

        self._scipy_started = False
        """true if scipy thread was started"""
        self._tmp_action = None
        self._tmp_action_index = 0

        self._scipy_thread = None
        """thread for running scipy optimize"""
        self._scipy_lock = threading.Lock()
        """lock for communication with scipy thread"""
        self._scipy_event = threading.Event()
        """event for signaling that model is finished"""
        self._scipy_state = self.ScipyState.created
        """scipy state"""
        self._scipy_x = None
        self._scipy_y = None
        self._scipy_log_transform = []
        self._scipy_lb = []
        self._scipy_ub = []
        self._scipy_diff_inc_rel = []
        self._scipy_diff_inc_abs = []
        self._scipy_res = None
        self._scipy_xy_log = []
        self._scipy_xj_log = []
        self._scipy_x_output_log = []
        self._scipy_iterations = []
        self._scipy_model_eval_num = 0

        self._tied_params_order = None

        super().__init__(**kwargs)

    def _set_bridge(self, bridge):
        """redirect bridge to wrapper"""
        bridge._set_new_link(self, self._get_output_to_wrapper)

    def _inicialize(self):
        """inicialize action run variables"""
        super()._inicialize()

        # update hash
        # todo:

        self.__make_output()

    def _get_output_to_wrapper(self):
        """return output relevant for wrapper action"""
        if 'WrappedAction' in self._variables and \
                isinstance(self._variables['WrappedAction'],  BaseActionType):
            ret = Struct()

            # static parameters
            try:
                if hasattr(self.get_input_val(0), "static_parameters"):
                    ret = self.get_input_val(0).static_parameters.duplicate()
            except ValueError:
                pass

            # parameters
            for par in self._variables['Parameters']:
                setattr(ret, par.name, Float())

            return ret
        return None

    def __make_output(self):
        """return output relevant for set action"""
        if self._is_state(ActionStateType.processed) or self._is_state(ActionStateType.finished):
            opt = Sequence(SingleIterationInfo.create_type(
                self._variables['Parameters'], self._variables['Observations']))

            # vector of weights
            obs_num = len(self._variables['Observations'])
            weights = np.zeros((obs_num, 1))
            for i in range(obs_num):
                weights[i] = self._variables['Observations'][i].weight

            for i in range(len(self._scipy_iterations)):
                # find output
                output = self._find_output_from_x(self._scipy_iterations[i][0])

                # get input from x
                input = self._scipy_x_to_wrapped_input(self._scipy_iterations[i][0])

                # find jacobian matrix
                jac_matrix = self._find_jac_matrix_from_x(self._scipy_iterations[i][0])

                par = Struct()
                sen_ind = 0
                for p in self._variables['Parameters']:
                    value = (getattr(input, p.name).value - p.offset) / p.scale
                    sen = np.nan
                    rel_sen = np.nan
                    if p.fixed:
                        pt = "Fixed"
                    elif p.tied_expression is not None:
                        pt = "Tied"
                    else:
                        pt = "Free"
                        if jac_matrix is not None:
                            sen = np.linalg.norm(jac_matrix[:, sen_ind] * weights) / obs_num
                            if p.log_transform:
                                rel_sen = sen * math.fabs(math.log10(value))
                            else:
                                rel_sen = sen * math.fabs(value)
                        sen_ind += 1
                    spo = Struct(parameter_type=Enum(["Free", "Tied", "Fixed", "Frozen"], pt),
                                 value=Float(value),
                                 interval_estimate=Tuple(Float(0.0), Float(0.0)),
                                 sensitivity=Float(sen),
                                 relative_sensitivity=Float(rel_sen))
                    setattr(par, p.name, spo)
                obs = Struct()
                sen_ind = 0
                for o in self._variables['Observations']:
                    m = getattr(self.get_input_val(0).observations, o.name).value
                    mv = getattr(output, o.name).value
                    if jac_matrix is not None:
                        sen = np.linalg.norm(jac_matrix[sen_ind, :]) * weights[sen_ind, 0] / self._scipy_x.shape[0]
                    else:
                        sen = np.nan
                    sen_ind += 1
                    soo = Struct(measured_value=Float(m),
                                 model_value=Float(mv),
                                 residual=Float(m - mv),
                                 sensitivity=Float(sen))
                    setattr(obs, o.name, soo)
                opt.add_item(Struct(iteration=Int(i + 1),
                                    cumulative_n_evaluation=Int(self._scipy_iterations[i][2]),
                                    residual=Float(self._scipy_iterations[i][1]),
                                    converge_reason=Enum(["none", "converged", "failure"], "none"),
                                    parameters=par,
                                    observations=obs))
            if self._scipy_res.success:
                cr = "converged"
            else:
                cr = "failure"
            res = Struct(n_iter=Int(len(self._scipy_iterations)),
                         converge_reason=Enum(["none", "converged", "failure"], cr),
                         residual=Float(self._scipy_res.fun))
            self._output = Struct(optimisation=opt, result=res)
        else:
            self._output = CalibrationOutputType.create_type(
                self._variables['Parameters'], self._variables['Observations'])

    def _get_variables_script(self): # ToDo:
        """return array of variables python scripts"""
        var = super()._get_variables_script()

        # WrappedAction
        if 'WrappedAction' in self._variables:
            wrapper = 'WrappedAction={0}'.format(self._variables['WrappedAction']._get_instance_name())
            var.append([wrapper])

        # Parameters
        v = ['Parameters=[']
        for par in self._variables['Parameters']:
            v.extend(Formater.indent(par._get_variables_script(), 4))
            v[-1] += ','
        if len(self._variables['Parameters']) > 0:
            v[-1] = v[-1][:-1]
        v.append(']')
        var.append(v)

        # Observations
        v = ['Observations=[']
        for obs in self._variables['Observations']:
            v.extend(Formater.indent(obs._get_variables_script(), 4))
            v[-1] += ','
        if len(self._variables['Observations']) > 0:
            v[-1] = v[-1][:-1]
        v.append(']')
        var.append(v)

        # AlgorithmParameters
        v = ['AlgorithmParameters=[']
        for par in self._variables['AlgorithmParameters']:
            v.extend(Formater.indent(par._get_variables_script(), 4))
            v[-1] += ','
        if len(self._variables['AlgorithmParameters']) > 0:
            v[-1] = v[-1][:-1]
        v.append(']')
        var.append(v)

        # TerminationCriteria
        v = self._variables['TerminationCriteria']._get_variables_script()
        v[0] = "TerminationCriteria=" + v[0]
        var.append(v)

        # MinimizationMethod
        if 'MinimizationMethod' in self._variables:
            v = "MinimizationMethod='{0}'".format(self._variables['MinimizationMethod'])
            var.append([v])

        # BoundsType
        if 'BoundsType' in self._variables:
            v = "BoundsType={0}".format(str(self._variables['BoundsType']))
            var.append([v])

        return var

    def _set_storing(self, identical_list):
        """set restore id"""
        super()._set_storing(identical_list)
        if 'WrappedAction' in self._variables:
            self._variables['WrappedAction']._set_storing(identical_list)

    def _plan_action(self, path):
        """
        If next action can be panned, return processed state and
        this action, else return processed state and null
        """
        if self._is_state(ActionStateType.processed):
            return ActionRunningState.wait,  None
        if self._is_state(ActionStateType.finished):
            return ActionRunningState.finished,  self
        if not self._scipy_started:
            if self._restore_id is not None:
                # restoring - set processed state as in classic action
                if self._is_state(ActionStateType.processed):
                    return ActionRunningState.wait,  None
                self._restore_results(path)
                if self._restore_id is not None:
                    self._set_state(ActionStateType.processed)
                    # send as short action for storing and settings state
                    return ActionRunningState.repeat,  self
            # run scipy thread
            self._scipy_thread = threading.Thread(target=self._scipy_run)
            self._scipy_thread.daemon = True
            self._scipy_thread.start()
            self._scipy_started = True
        while True:
            if self._get_scipy_state() == self.ScipyState.running:
                if self._scipy_event.is_set():
                    return ActionRunningState.wait, None
                else:
                    if self._tmp_action is None:
                        self._tmp_action = self._create_tmp_action(self._scipy_x_to_wrapped_input(self._scipy_x))
                    state, action = self._tmp_action._plan_action(path)
                    if state is ActionRunningState.finished:
                        output = action._get_output()
                        self._scipy_y = self._wrapped_output_to_scipy_y(output, self._scipy_x)
                        self._tmp_action = None
                        self._scipy_event.set()
                        return ActionRunningState.wait, None
                    if state is ActionRunningState.repeat:
                        return state, action
                    if state is ActionRunningState.error:
                        return state, action
                    if state is ActionRunningState.wait and action is not None:
                        return ActionRunningState.repeat, action
            if self._get_scipy_state() == self.ScipyState.finished:
                self._set_state(ActionStateType.processed)
                self.__make_output()
                return ActionRunningState.repeat, self
            return ActionRunningState.wait, None
        return ActionRunningState.wait, None

    def _create_tmp_action(self, input):
        self._tmp_action_index += 1

        gen = VariableGenerator(Variable=input)
        gen._inicialize()
        gen._update()
        gen._after_update(None)
        # if self._inputs[j]._restore_id is not None:
        #     # input is restored => mark generator as restored
        #     gen._set_restored()
        inputs = [gen]
        name = self._variables['WrappedAction']._get_instance_name()
        script = self._variables['WrappedAction']._get_settings_script()
        script.insert(0, "from Analysis.pipeline import *")
        script = '\n'.join(script)
        script = script.replace(name, "new_dupl_workflow")
        exec(script, globals())
        new_dupl_workflow.set_inputs(inputs)
        new_dupl_workflow._inicialize()
        new_dupl_workflow._reset_storing(
            self._variables['WrappedAction'], self._index_iden + "_" + str(self._tmp_action_index))
        return new_dupl_workflow

    def _check_params(self):
        """check if all require params is set"""
        err = super()._check_params()

        # Parameters
        if 'Parameters' in self._variables:
            if isinstance(self._variables['Parameters'], list):
                for i in range(len(self._variables['Parameters'])):
                    if isinstance(self._variables['Parameters'][i], CalibrationParameter):
                        if self._variables['Parameters'][i].bounds[0] > self._variables['Parameters'][i].bounds[1]:
                            self._add_error(err, "Parameter 'Parameters[{0}]': Upper bound must be greater or equal to lower bound".format(str(i)))
                        if self._variables['Parameters'][i].init_value < self._variables['Parameters'][i].bounds[0]:
                            self._add_error(err, "Parameter 'Parameters[{0}]': Init value must be greater or equal to lower bound".format(str(i)))
                        if self._variables['Parameters'][i].init_value > self._variables['Parameters'][i].bounds[1]:
                            self._add_error(err, "Parameter 'Parameters[{0}]': Init value must be lower or equal to upper bound".format(str(i)))
                        if self._variables['Parameters'][i].log_transform:
                            if self._variables['Parameters'][i].init_value <= 0:
                                self._add_error(err, "Parameter 'Parameters[{0}]': Init value must be positive, if log transform is chosen".format(str(i)))
                            if self._variables['Parameters'][i].bounds[0] <= 0:
                                self._add_error(err, "Parameter 'Parameters[{0}]': Lower bound must be positive, if log transform is chosen".format(str(i)))
                            if self._variables['Parameters'][i].bounds[1] <= 0:
                                self._add_error(err, "Parameter 'Parameters[{0}]': Upper bound must be positive, if log transform is chosen".format(str(i)))
                        if self._variables['Parameters'][i].fixed and self._variables['Parameters'][i].tied_expression is not None:
                            self._add_error(err, "Parameter 'Parameters[{0}]': Fixed can't be tied".format(str(i)))
                    else:
                        self._add_error(err, "Type of parameter 'Parameters[{0}]' must be CalibrationParameter".format(str(i)))
                self._extend_error(err, self.__check_tied_parameters(self._variables['Parameters']))
            else:
                self._add_error(err, "Parameter 'Parameters' must be list of CalibrationParameter")
        else:
            self._add_error(err, "Parameter 'Parameters' is required")

        # Observations
        if 'Observations' in self._variables:
            if isinstance(self._variables['Observations'], list):
                for i in range(len(self._variables['Observations'])):
                    if not isinstance(self._variables['Observations'][i], CalibrationObservation):
                        self._add_error(err, "Type of parameter 'Observations[{0}]' must be CalibrationObservation".format(str(i)))
            else:
                self._add_error(err, "Parameter 'Observations' must be list of CalibrationObservation")
        else:
            self._add_error(err, "Parameter 'Observations' is required")

        # AlgorithmParameters
        if 'AlgorithmParameters' in self._variables:
            if isinstance(self._variables['AlgorithmParameters'], list):
                for i in range(len(self._variables['AlgorithmParameters'])):
                    if not isinstance(self._variables['AlgorithmParameters'][i], CalibrationAlgorithmParameter):
                        self._add_error(err, "Type of parameter 'AlgorithmParameters[{0}]' must be CalibrationAlgorithmParameter".format(str(i)))
            else:
                self._add_error(err, "Parameter 'AlgorithmParameters' must be list of CalibrationAlgorithmParameter")
        else:
            self._add_error(err, "Parameter 'AlgorithmParameters' is required")

        # TerminationCriteria
        if 'TerminationCriteria' in self._variables:
            if not isinstance(self._variables['TerminationCriteria'], CalibrationTerminationCriteria):
                self._add_error(err, "Parameter 'TerminationCriteria' must be CalibrationTerminationCriteria")
        else:
            self._add_error(err, "Parameter 'TerminationCriteria' is required")
        if len(self._inputs) == 0:
            self._add_error(err, "No input action for Calibration")

        # MinimizationMethod
        if 'MinimizationMethod' in self._variables:
            if isinstance(self._variables['MinimizationMethod'], str):
                if not self._variables['MinimizationMethod'] in ["L-BFGS-B", "SLSQP", "DIFF"]:
                    self._add_error(err, "Method '{0}' is not supported.".format(self._variables['MinimizationMethod']))
            else:
                self._add_error(err, "Parameter 'MinimizationMethod' must be string")

        # BoundsType
        if 'BoundsType' in self._variables:
            if isinstance(self._variables['BoundsType'], CalibrationBoundsType):
                if not self._variables['BoundsType'] in [CalibrationBoundsType.hard, CalibrationBoundsType.soft]:
                    self._add_error(err, "Bounds type '{0}' is not supported.".format(self._variables['BoundsType']))
            else:
                self._add_error(err, "Parameter 'BoundsType' must be CalibrationBoundsType")

        # WrappedAction
        if 'WrappedAction' in self._variables:
            if not isinstance(self._variables['WrappedAction'], Workflow):
                self._add_error(err, "Parameter 'WrappedAction' must be Workflow")

        for par in self._variables['Parameters']:
            f = False
            for alg in self._variables['AlgorithmParameters']:
                if par.group == alg.group:
                    f = True
                    break
            if not f:
                self._add_error(err, "Algorithm parameter for group '{0}' must be in AlgorithmParameters".format(par.group))

        # check inputs
        if len(self._inputs) != 1:
            self._add_error(err, "Calibration must have one Input action.")
        input = self.get_input_val(0)
        if isinstance(input, Struct):
            try:
                if hasattr(input, "observations"):
                    for obs in self._variables['Observations']:
                        try:
                            if hasattr(input.observations, obs.name):
                                pass
                        except ValueError:
                            self._add_error(err, "In Input missing observation '{0}'.".format(obs.name))
                    ret = input.observations.duplicate()
            except ValueError:
                self._add_error(err, "Input Struct must have attribute 'observations'.")
        else:
            self._add_error(err, "Input action not produce Struct type variable.")

        return err

    def __check_tied_parameters(self, parameters):
        """check tied parameters"""
        err = []
        parameters_list = []
        for par in parameters:
            parameters_list.append(par.name)
        for par in parameters:
            if par.tied_expression is not None:
                if par.tied_params is None or len(par.tied_params) < 1:
                    self._add_error(err, "Tied parameter '{0}' must have at least one parameter".format(par.name))
                for p in par.tied_params:
                    if p not in parameters_list:
                        self._add_error(err, "Tied parameter '{0}' have parameter '{1}' which is not in Parameters".format(par.name, p))

        # check circular dependencies
        self._tied_params_order = self._get_tied_params_order(parameters)
        if self._tied_params_order is None:
            self._add_error(err, "Tied parameters have circular dependencies")

        return err

    def _get_tied_params_order(self, parameters):
        """sort tied params to right evaluation order"""
        tpar = []
        for par in parameters:
            if par.tied_expression is not None:
                tpar.append(par)
        opar = []
        while len(tpar) > 0:
            f = False
            for i in range(len(tpar)):
                p = tpar.pop(0)
                d = False
                for r in p.tied_params:
                    for s in tpar:
                        if r == s.name:
                            d = True
                            break
                    if d:
                        break
                if d:
                    tpar.append(p)
                else:
                    opar.append(p.name)
                    f = True
                    break
            if not f:
                return None
        return opar

    def validate(self):
        """validate variables, input and output"""
        err = super().validate()
        if 'WrappedAction' in self._variables and \
                isinstance(self._variables['WrappedAction'], BaseActionType):
            err.extend(self._variables['WrappedAction'].validate())
        return err

    def _get_statistics(self):  # ToDo:
        """return all statistics for this and child action"""
        stat = self._variables['WrappedAction']._get_statistics()
        number = self._scipy_model_eval_num
        ret = ActionsStatistics()
        ret.add(stat, number)
        return ret

    def _get_scipy_state(self):
        """get scipy state"""
        with self._scipy_lock:
            return self._scipy_state

    def _set_scipy_state(self, state):
        """set scipy state"""
        with self._scipy_lock:
            self._scipy_state = state

    def _scipy_run(self): # todo:
        """run scipy minimalization"""
        init_values = []
        alg_par = {}
        for par in self._variables['AlgorithmParameters']:
            alg_par[par.group] = par
        self._scipy_log_transform = []
        self._scipy_lb = []
        self._scipy_ub = []
        self._scipy_diff_inc_rel = []
        self._scipy_diff_inc_abs = []
        for par in self._variables['Parameters']:
            if not par.fixed and par.tied_expression is None:
                self._scipy_log_transform.append(par.log_transform)
                if par.log_transform:
                    init_values.append(math.log10(par.init_value))
                    self._scipy_lb.append(math.log10(par.bounds[0]))
                    self._scipy_ub.append(math.log10(par.bounds[1]))
                else:
                    init_values.append(par.init_value)
                    self._scipy_lb.append(par.bounds[0])
                    self._scipy_ub.append(par.bounds[1])
                self._scipy_diff_inc_rel.append(alg_par[par.group].diff_inc_rel)
                self._scipy_diff_inc_abs.append(alg_par[par.group].diff_inc_abs)
        x0 = np.array(init_values)
        args = {}
        if 'BoundsType' not in self._variables or \
                self._variables['BoundsType'] == CalibrationBoundsType.hard:
            args["bounds"] = tuple(zip(self._scipy_lb, self._scipy_ub))

        # ToDo: if all pars are fixed change behavior

        self._scipy_event.set()
        self._set_scipy_state(self.ScipyState.running)

        # self._scipy_res = minimize(self._scipy_fun, x0, method='L-BFGS-B', jac=self._scipy_jac, callback=self._scipy_callback,
        #                            options={'maxiter': self._variables['TerminationCriteria'].n_max_steps,
        #                                     'ftol': 1e-6, 'disp': True}, **args)

        if self._variables['MinimizationMethod'] == "DIFF":
            self._scipy_res = differential_evolution(self._scipy_fun, strategy= "best1bin",
                                                     maxiter=self._variables['TerminationCriteria'].n_max_steps,
                                                     popsize=5, tol=1e-4, callback=self._scipy_callback,
                                                     disp=True, polish=False, **args)
        elif self._variables['MinimizationMethod'] == "L-BFGS-B":
            self._scipy_res = min_lbfgsb(self._scipy_fun, x0, jac=self._scipy_jac, callback=self._scipy_callback,
                                         disp=True, ter_crit=self._variables['TerminationCriteria'], **args)
        else:
            self._scipy_res = min_slsqp(self._scipy_fun, x0, jac=self._scipy_jac, callback=self._scipy_callback,
                                         disp=True, ter_crit=self._variables['TerminationCriteria'], **args)

        # if result differ from last iteration create last iteration from it
        if not np.all(self._scipy_res.x == self._scipy_iterations[-1][0]):
            self._scipy_callback(self._scipy_res.x)

        self._set_scipy_state(self.ScipyState.finished)

        #print("scipy_model_eval_num = {}".format(str(self._scipy_model_eval_num)))
        #print("x = {}".format(str(self._scipy_res.x)))

    def _scipy_fun(self, x):
        """objective function called by scipy"""
        #print("_scipy_fun enter")
        #print(x)
        y = self._scipy_model_eval(x)
        #print("y: {}".format(y))

        return y

    def _scipy_jac(self, x):
        """jacobian function called by scipy"""
        #print("_scipy_jac enter")
        fx = self._scipy_model_eval(x)

        # observations in x
        obs_num = len(self._variables['Observations'])
        obs_x = np.zeros((obs_num, 1))
        output = self._find_output_from_x(x)
        ind = 0
        for obs in self._variables['Observations']:
            obs_x[ind] = getattr(output, obs.name).value
            ind += 1

        jac = np.zeros_like(x)
        jac_matrix = np.zeros((obs_num, x.shape[0]))
        for i in range(x.shape[0]):
            if self._scipy_log_transform[i]:
                h = self._scipy_diff_inc_rel[i] * math.fabs(math.pow(10.0, x[i])) + self._scipy_diff_inc_abs[i]
                xh = x.copy()
                xh[i] = math.log10(math.pow(10.0, xh[i]) + h)
                jac[i] = (self._scipy_model_eval(xh) - fx) / (xh[i] - x[i])
            else:
                h = self._scipy_diff_inc_rel[i] * math.fabs(x[i]) + self._scipy_diff_inc_abs[i]
                xh = x.copy()
                xh[i] += h
                jac[i] = (self._scipy_model_eval(xh) - fx) / h

            # observations in xh
            obs_xh = np.zeros((obs_num, 1))
            output = self._find_output_from_x(xh)
            ind = 0
            for obs in self._variables['Observations']:
                obs_xh[ind] = getattr(output, obs.name).value
                ind += 1

            jac_matrix[:, i] = ((obs_xh - obs_x) / (xh[i] - x[i])).reshape(obs_num)
        self._scipy_xj_log.append((x.copy(), jac_matrix))
        return jac

    def _scipy_callback(self, xk, convergence=None):
        """called by scipy after each iteration"""
        self._scipy_iterations.append((xk.copy(), self._scipy_model_eval(xk), self._scipy_model_eval_num))
        #print(self._scipy_iterations[-1])
        #print("conv: {}".format(convergence))

    def _scipy_model_eval(self, x):
        """model evaluation used in _scipy_fun and _scipy_jac"""
        for xy in self._scipy_xy_log:
            if np.all(xy[0] == x):
                return xy[1]

        self._scipy_model_eval_num += 1
        self._scipy_x = x
        self._scipy_event.clear()
        self._scipy_event.wait()
        self._scipy_xy_log.append((x.copy(), self._scipy_y))
        return self._scipy_y

    def _scipy_x_to_wrapped_input(self, x):
        """convert x from scipy format to workflow format"""
        ret = Struct()

        # static parameters
        try:
            if hasattr(self.get_input_val(0), "static_parameters"):
                ret = self.get_input_val(0).static_parameters.duplicate()
        except ValueError:
            pass

        par_dict = {}
        ind = 0
        for par in self._variables['Parameters']:
            if par.tied_expression is not None:
                continue
            if par.fixed:
                v = par.init_value
            else:
                v = x[ind]
                ind += 1
                if par.log_transform:
                    v = math.pow(10.0, v)
            par_dict[par.name] = v
            v = par.scale * v + par.offset
            setattr(ret, par.name, Float(v))

        # tied params
        if self._tied_params_order is None:
            self._tied_params_order = self._get_tied_params_order(self._variables['Parameters'])
        if self._tied_params_order is not None:
            for tp in self._tied_params_order:
                par = None
                for r in self._variables['Parameters']:
                    if tp == r.name:
                        par = r
                        break
                v = eval(par.tied_expression, globals(), par_dict)
                par_dict[par.name] = v
                v = par.scale * v + par.offset
                setattr(ret, par.name, Float(v))

        return ret

    def _wrapped_output_to_scipy_y(self, output, x):
        """convert output from workflow to scipy objective value"""
        # log
        self._scipy_x_output_log.append((x.copy(), output))

        ret = 0.0
        for obs in self._variables['Observations']:
            mo = getattr(output, obs.name).value
            ret += (getattr(self.get_input_val(0).observations, obs.name).value - mo)**2 * obs.weight**2

            # observation bounds
            if obs.upper_bound is not None and mo > obs.upper_bound:
                ret += (mo - obs.upper_bound)**2 * 1e+3 * obs.weight**2
            if obs.lower_bound is not None and mo < obs.lower_bound:
                ret += (obs.lower_bound - mo)**2 * 1e+3 * obs.weight**2

        if 'BoundsType' in self._variables and \
                self._variables['BoundsType'] == CalibrationBoundsType.soft:
            lb = self._scipy_lb
            ub = self._scipy_ub
            c = 1e+6
            for i in range(x.shape[0]):
                if x[i] < lb[i]:
                    ret += ((lb[i] - x[i]) / (ub[i] - lb[i]))**2 * c
                if x[i] > ub[i]:
                    ret += ((x[i] - ub[i]) / (ub[i] - lb[i]))**2 * c

        return ret

    def _find_output_from_x(self, x):
        """find output from x"""
        output = None
        for o in self._scipy_x_output_log:
            if np.all(o[0] == x):
                output = o[1]
                break
        return output

    def _find_jac_matrix_from_x(self, x):
        """find jacobian matrix from x"""
        jac = None
        for j in self._scipy_xj_log:
            if np.all(j[0] == x):
                jac = j[1]
                break
        return jac
