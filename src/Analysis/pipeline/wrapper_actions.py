from .action_types import WrapperActionType, ActionStateType, BaseActionType, ActionsStatistics, ActionRunningState
from .data_types_tree import Ensemble, DTT
from .generator_actions import VariableGenerator
from .workflow_actions import Workflow
from .data_types_tree import Struct, Float
from .calibration_data_types import *
from .calibration_lbfgsb import min_lbfgsb
from .calibration_slsqp import min_slsqp

import threading
import time
from enum import IntEnum
import math

import numpy as np
from scipy.optimize import minimize


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
                script.insert(0, "from pipeline import *")
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
            return ActionRunningState.repeat, self
        next_wa = self._procesed_instances
        while next_wa < len(self._wa_instances):    
            state, action = self._wa_instances[next_wa]._plan_action(path)
            if state is ActionRunningState.finished:
                if next_wa == self._procesed_instances:
                    self._procesed_instances += 1
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

    def _after_update(self, store_dir):    
        """
        Set real output variable and set finished state.
        """
        self.__make_output()
        self._store_results(store_dir)
        self._set_state(ActionStateType.finished)

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
        #waiting = 2
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
        :param CalibrationOutputType Output: output from calibration
        :param Action Input: action that return input to calibration
        """

        self._wa_instances = []
        """
        Set wrapper class serve only as template, for run is make
        copy of this class. The variable is for the copies.
        """
        self._procesed_instances = 0
        """How many instances is procesed"""
        self._tmp_action = None

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
        self._scipy_lb = []
        self._scipy_ub = []
        self._scipy_diff_inc_rel = []
        self._scipy_diff_inc_abs = []
        self._scipy_res = None
        self._scipy_xy_log = []
        self._scipy_x_output_log = []
        self._scipy_iterations = []
        self._scipy_model_eval_num = 0

        super().__init__(**kwargs)

    def _set_bridge(self, bridge):
        """redirect bridge to wrapper"""
        bridge._set_new_link(self, self._get_output_to_wrapper)

    def _inicialize(self):
        """inicialize action run variables"""
        super()._inicialize()
        self.__make_output()

    def _get_output_to_wrapper(self):  # ToDo:
        """return output relevant for wrapper action"""
        if 'WrappedAction' in self._variables and \
            isinstance(self._variables['WrappedAction'],  BaseActionType):
            return Struct(vodivost=Float(), tlak=Float())
            #return Struct(X1=Float(), X2=Float(), X3=Float(), A=Float(), B=Float())
            # for wraped action return previous input
            ensemble = self.get_input_val(0)
            if isinstance(ensemble,  Ensemble):
                return ensemble.subtype
        return None

    def __make_output(self):  # ToDo:
        """return output relevant for set action"""
        if self._is_state(ActionStateType.finished):
            opt = Sequence(SingleIterationInfo.create_type(self._variables['Parameters'], self._variables['Observations']))
            for i in range(len(self._scipy_iterations)):
                # find output
                output = None
                for o in self._scipy_x_output_log:
                    if np.all(o[0] == self._scipy_iterations[i][0]):
                        output = o[1]
                        break

                input = self._scipy_x_to_wrapped_input(self._scipy_iterations[i][0])

                par = Struct()
                for p in self._variables['Parameters']:
                    if p.fixed:
                        pt = "Fixed"
                    else:
                        pt = "Free"
                    spo = Struct(parameter_type=Enum(["Free", "Tied", "Fixed", "Frozen"], pt),
                                 value=getattr(input, p.name),
                                 interval_estimate=Tuple(Float(0.0), Float(0.0)),
                                 sensitivity=Float(0.0),
                                 relative_sensitivity=Float(0.0))
                    setattr(par, p.name, spo)
                obs = Struct()
                for o in self._variables['Observations']:
                    m = getattr(self.get_input_val(0).observations, o.name).value
                    mv = getattr(output, o.name).value
                    soo = Struct(measured_value=Float(m),
                                 model_value=Float(mv),
                                 residual=Float(m - mv),
                                 sensitivity=Float(0.0))
                    setattr(obs, o.name, soo)
                opt.add_item(Struct(iteration=Int(i),
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
            print("\n".join(self._output._get_settings_script()))
        else:
            self._output = CalibrationOutputType.create_type(self._variables['Parameters'], self._variables['Observations'])

    def _get_variables_script(self):
        """return array of variables python scripts"""
        var = super._get_variables_script()
        if 'WrappedAction' in self._variables:
            wrapper = 'WrappedAction={0}'.format(self._variables['WrappedAction']._get_instance_name())
            var.append([wrapper])
        return var

    def _set_storing(self, identical_list):
        """set restore id"""
        super._set_storing(identical_list)
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
        if len(self._wa_instances) == 0:
            # ToDo: promyslet
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
            # ensemble = []
            # for i in range(0, len(self._inputs)):
            #     ensemble.append(self.get_input_val(i))
            # if len(ensemble[0])== 0:
            #     return ActionRunningState.error,  \
            #         ["Empty Ensemble in ForEach input"]
            # for i in range(0, len(ensemble[0]._list)):
            #     inputs = []
            #     for j in range(0, len(self._inputs)):
            #         if len(ensemble[j])<=i:
            #             return ActionRunningState.error,  \
            #                 ["Ensamble in Input({0}) has less items".format(str(i))]
            #         gen = VariableGenerator(Variable=ensemble[j]._list[i])
            #         gen._inicialize()
            #         gen._update()
            #         gen._after_update(None)
            #         if self._inputs[j]._restore_id is not None:
            #             # input is restored => mark generator as restored
            #             gen._set_restored()
            #         inputs.append(gen)
            #     name = self._variables['WrappedAction']._get_instance_name()
            #     script = self._variables['WrappedAction']._get_settings_script()
            #     script.insert(0, "from pipeline import *")
            #     script = '\n'.join(script)
            #     script = script.replace(name, "new_dupl_workflow")
            #     exec (script, globals())
            #     self._wa_instances.append(new_dupl_workflow)
            #     self._wa_instances[-1].set_inputs(inputs)
            #     self._wa_instances[-1]._inicialize()
            #     self._wa_instances[-1]._reset_storing(
            #         self._variables['WrappedAction'], self._index_iden +"_"+ str(i))
            self._wa_instances.append(1)
        if self._procesed_instances == len(self._wa_instances):
            for instance in self._wa_instances:
                #if not instance._is_state(ActionStateType.finished):
                    return ActionRunningState.wait, None
            self._set_state(ActionStateType.processed)
            return ActionRunningState.repeat, self
        next_wa = self._procesed_instances
        while True:#next_wa < len(self._wa_instances):
            if self._get_scipy_state() == self.ScipyState.running:
                if self._scipy_event.is_set():
                    return ActionRunningState.wait, None
                else:
                    if self._tmp_action is None:
                        self._tmp_action = self._create_tmp_action(self._scipy_x_to_wrapped_input(self._scipy_x))
                    state, action = self._tmp_action._plan_action(path)
                    if state is ActionRunningState.finished:
                        # if next_wa == self._procesed_instances:
                        # self._procesed_instances += 1
                        output = action._get_output()
                        self._scipy_y = self._wrapped_output_to_scipy_y(output, self._scipy_x)
                        self._tmp_action = None
                        #self._set_scipy_state(self.ScipyState.running)
                        self._scipy_event.set()
                        return ActionRunningState.wait, None
                    if state is ActionRunningState.repeat:
                        return state, action
                    if state is ActionRunningState.error:
                        return state, action
                    if state is ActionRunningState.wait and action is not None:
                        return ActionRunningState.repeat, action
            if self._get_scipy_state() == self.ScipyState.finished:
                self._set_state(ActionStateType.finished)
                self.__make_output()
                return ActionRunningState.wait, None
            #state, action = self._wa_instances[next_wa]._plan_action(path)
            #state = ActionRunningState.finished
            #action = None
            # run return wait, try next
            #next_wa += 1
            return ActionRunningState.wait, None
        return ActionRunningState.wait, None

    def _create_tmp_action(self, input):
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
        script.insert(0, "from pipeline import *")
        script = '\n'.join(script)
        script = script.replace(name, "new_dupl_workflow")
        exec(script, globals())
        new_dupl_workflow.set_inputs(inputs)
        new_dupl_workflow._inicialize()
        #new_dupl_workflow._reset_storing(
            #self._variables['WrappedAction'], self._index_iden + "_" + str(i))
        return new_dupl_workflow

    def _after_update(self, store_dir):
        """
        Set real output variable and set finished state.
        """
        self.__make_output()
        self._store_results(store_dir)
        self._set_state(ActionStateType.finished)

    def _check_params(self):
        """check if all require params is set"""
        err = super()._check_params()
        if 'Parameters' in self._variables:
            if isinstance(self._variables['Parameters'], list):
                for i in range(len(self._variables['Parameters'])):
                    if isinstance(self._variables['Parameters'][i], CalibrationParameter):
                        if self._variables['Parameters'][i].bounds[0] > self._variables['Parameters'][i].bounds[1]:
                            self._add_error(err, "Parameter 'Parameters[{0}]': Upper bound must be greater or equal to lower bound".format(str(i)))
                    else:
                        self._add_error(err, "Type of parameter 'Parameters[{0}]' must be CalibrationParameter".format(str(i)))
            else:
                self._add_error(err, "Parameter 'Parameters' must be list of CalibrationParameter")
        else:
            self._add_error(err, "Parameter 'Parameters' is required")
        if 'Observations' in self._variables:
            if isinstance(self._variables['Observations'], list):
                for i in range(len(self._variables['Observations'])):
                    if not isinstance(self._variables['Observations'][i], CalibrationObservation):
                        self._add_error(err, "Type of parameter 'Observations[{0}]' must be CalibrationObservation".format(str(i)))
            else:
                self._add_error(err, "Parameter 'Observations' must be list of CalibrationObservation")
        else:
            self._add_error(err, "Parameter 'Observations' is required")
        if 'AlgorithmParameters' in self._variables:
            if isinstance(self._variables['AlgorithmParameters'], list):
                for i in range(len(self._variables['AlgorithmParameters'])):
                    if not isinstance(self._variables['AlgorithmParameters'][i], CalibrationAlgorithmParameter):
                        self._add_error(err, "Type of parameter 'AlgorithmParameters[{0}]' must be CalibrationAlgorithmParameter".format(str(i)))
            else:
                self._add_error(err, "Parameter 'AlgorithmParameters' must be list of CalibrationAlgorithmParameter")
        else:
            self._add_error(err, "Parameter 'AlgorithmParameters' is required")
        if 'TerminationCriteria' in self._variables:
            if not isinstance(self._variables['TerminationCriteria'], CalibrationTerminationCriteria):
                self._add_error(err, "Parameter 'TerminationCriteria' must be CalibrationTerminationCriteria")
        else:
            self._add_error(err, "Parameter 'TerminationCriteria' is required")
        if len(self._inputs) == 0:
            self._add_error(err, "No input action for Calibration")
        if 'MinimizationMethod' in self._variables:
            if isinstance(self._variables['MinimizationMethod'], str):
                if not self._variables['MinimizationMethod'] in ["L-BFGS-B", "SLSQP"]:
                    self._add_error(err, "Method '{0}' is not supported.".format(self._variables['MinimizationMethod']))
            else:
                self._add_error(err, "Parameter 'MinimizationMethod' must be string")
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

        # ToDo: check inputs
        # for i in range(len(self._inputs)):
        #     ensemble = self.get_input_val(i)
        #     if not isinstance(ensemble, Ensemble):
        #         self._add_error(err, "Input action {0} not produce Ensemble type variable".format(str(i)))
        return err

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
        number = 0
        if len(self._wa_instances)>0:
            number = len(self._wa_instances)
        else:
            ensemble = self.get_input_val(0)
            #number = len(ensemble)
        ret = ActionsStatistics()
        ret.add(stat, number)
        return ret

    def _get_scipy_state(self):
        with self._scipy_lock:
            return self._scipy_state

    def _set_scipy_state(self, state):
        with self._scipy_lock:
            self._scipy_state = state

    def _scipy_run(self):
        init_values = []
        alg_par = {}
        for par in self._variables['AlgorithmParameters']:
            alg_par[par.group] = par
        for par in self._variables['Parameters']:
            if not par.fixed:
                init_values.append(par.init_value)
                self._scipy_lb.append(par.bounds[0])
                self._scipy_ub.append(par.bounds[1])
                self._scipy_diff_inc_rel.append(alg_par[par.group].diff_inc_rel)
                self._scipy_diff_inc_abs.append(alg_par[par.group].diff_inc_abs)
        x0 = np.array(init_values)

        # ToDo: if all pars are fixed change behavior

        self._scipy_event.set()
        self._set_scipy_state(self.ScipyState.running)

        self._scipy_res = minimize(self._scipy_fun, x0, method='L-BFGS-B', jac=self._scipy_jac, callback=self._scipy_callback,
                                   options={'maxiter': self._variables['TerminationCriteria'].n_max_steps,
                                            'ftol': 1e-6, 'disp': True})

        # if self._variables['MinimizationMethod'] == "L-BFGS-B":
        #     self._scipy_res = min_lbfgsb(self._scipy_fun, x0, jac=self._scipy_jac, callback=self._scipy_callback,
        #                                  disp=True, ter_crit=self._variables['TerminationCriteria'])
        # else:
        #     self._scipy_res = min_slsqp(self._scipy_fun, x0, jac=self._scipy_jac, callback=self._scipy_callback,
        #                                  disp=True, ter_crit=self._variables['TerminationCriteria'])

        self._set_scipy_state(self.ScipyState.finished)

        print("scipy_model_eval_num = {}".format(str(self._scipy_model_eval_num)))
        print("x = {}".format(str(self._scipy_res.x)))

    def _scipy_fun(self, x):
        print("_scipy_fun enter")
        print(x)
        y = self._scipy_model_eval(x)
        print(y)

        return y

    def _scipy_jac(self, x):
        print("_scipy_jac enter")
        fx = self._scipy_model_eval(x)
        jac = np.zeros_like(x)
        for i in range(x.shape[0]):
            h = self._scipy_diff_inc_rel[i] * x[i] + self._scipy_diff_inc_abs[i]
            xh = x.copy()
            xh[i] += h
            jac[i] = (self._scipy_model_eval(xh) - fx) / h
        return jac

    def _scipy_callback(self, xk):
        self._scipy_iterations.append((xk.copy(), self._scipy_model_eval(xk), self._scipy_model_eval_num))

    def _scipy_model_eval(self, x):
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
        mod_par = Struct()
        ind = 0
        for par in self._variables['Parameters']:
            if par.fixed:
                v = par.init_value
            else:
                v = x[ind]
            if par.log_transform:
                v = math.exp(v)
            v = par.scale * v + par.offset
            setattr(mod_par, par.name, Float(v))
            ind += 1
        #ret = Struct(parameters=mod_par)
        ret = mod_par

        # if hasattr(self.get_input_val(0), "data"):
        #     ret.data = self.get_input_val(0).data

        return ret

    def _wrapped_output_to_scipy_y(self, output, x):
        # log
        self._scipy_x_output_log.append((x.copy(), output))

        ret = 0.0
        for obs in self._variables['Observations']:
            ret += (getattr(self.get_input_val(0).observations, obs.name).value - getattr(output, obs.name).value)**2 * obs.weight**2

        lb = self._scipy_lb
        ub = self._scipy_ub
        c = 1e+6
        for i in range(x.shape[0]):
            if x[i] < lb[i]:
                ret += ((lb[i] - x[i]) / (ub[i] - lb[i]))**2 * c
            if x[i] > ub[i]:
                ret += ((x[i] - ub[i]) / (ub[i] - lb[i]))**2 * c

        return ret
