import inspect
import importlib

"""
Minimalistic implementation of the analysis data layer for the GUI.

TODO:
- ActionBase  with connections, representation and basic evaluation support
-
"""

class ActionInput:
    """
    Single
    """

class _ActionBase:
    __n_parameters = -1
    """ Number of parameters of the action. -1 for variable number."""

    """
    Single node of the DAG of a single Workflow.
    """
    def __init__(self, inputs=[], config=None, name=None):
        #assert hasattr(self, "__action_parameters")
        #self.__parameter_dict = { for i, (name, type) in self.__action_parameters}
        self.set_inputs(inputs)
        """ List of action instances connected to the input, predecessors in the workflow DAG. 
            Temporary solution. TODO: After Types are at least partially implemented we can use a Class instead of the 
            list in order to have named parameters, or even allow passing more parameters directly.
        """
        self.config = config
        """ Action configuration as a data tree. 
            
            Not clear if we need to know it explicitely on abstract level, 
        but probably yes because of action hashing mechanisms."""
        self.instance_name = name
        """ Unique ID within the workspace. Checked and updated during the workspace construction."""
        self.output_actions = []
        """ Actions connected to the output. Set during the workflow construction."""


    @property
    def n_parameters(self):
        return self.__n_parameters


    @property
    def action_name(self):
        return self.__class__.name


    def name(self, instance_name):
        """
        Attribute setter. Usage:
        my_instance = SomeAction(inputs).name("instance_name")

        should be almost equivalent to:

        var.instance_name = SomeAction(inputs)

        :param instance_name:
        :return:
        """
        self.instance_name = instance_name
        return self

    def set_inputs(self, inputs):
        if self.n_parameters > -1:
            assert len(inputs) == self.n_parameters
        self._inputs = inputs


    def _code(self, inputs, config=None):
        """
        Return a representation of the action instance.
        This is generic representation code that calls the constructor.

        Two

        :param inputs: Dictionary assigning strings to the Action's parameters.
        :param config: String used for configuration, call serialization of the configuration by default.
        :return: string (code to instantiate the action)
        """
        input_params = ", ".join([ "{}={}".format(param, inputs[param]) for param in self.input_type.keys()])
        if config is None:
            config = types.serialize_code(self.config)
        if config is None:
            return "{}({})".format(self.action_name, input_params)
        else:
            return "{}( {}, config={})".format(self.action_name, input_params, config)

    def evaluate(self, inputs):
        """
        Pure virtual method.
        If the validate method is defined it is used for type compatibility validation otherwise
        this method must handle both a type tree and the data tree on the input
        returning the appropriate output type tree or the data tree respectively.
        :param inputs:
        :return:
        """
        assert False, "Implementation has to be provided."

    @property
    def input_type(self):
        """
        Return a Class of the action named inputs.
        :return: types.Class instance
        """
        pass

    def validate(self, inputs):
        return self.evaluate(inputs)


class _Slot(_ActionBase):
    def __init__(self, i_slot, slot_name=None):
        """
        Auxiliary action to connect to a named input slot of the workflow.
        :param slot_name:
        """
        super().__init__(name=slot_name)
        self.rank = i_slot
        """ Slot rank. """
        self.type = None
        """ Slot type. None - slot not used. """

    def is_used(self):
        return bool(self.output_actions)





class _WorkflowBase(_ActionBase):
    """
    Every workflow is a class derived from this base.
    """
    _result = None
    """  Result subaction.  """
    _slots = {}
    """ Input slots of the workflow DAG. """
    _actions = {}
    """ Dict:  unique action instance name -> action instance """

    @classmethod
    def _dfs(cls, root_action, previsit=None, postvisit=None, edge_visit=None):
        """
        Generic DFS for the action DAG.
        :param root_action:
        :return:
        """
        action_ids = set()
        action_stack = [root_action]
        while action_stack:
            action = action_stack.pop(-1)
            if previsit:
                previsit(action)
            for input_action in action._inputs:
                assert isinstance(input_action, _ActionBase)
                if edge_visit:
                    edge_visit(input_action, action)
                action_id = id(input_action)
                if action_id not in action_ids:
                    action_stack.append(input_action)
            if postvisit:
                postvisit(action)


    @classmethod
    def _construct(cls, result, slots):
        """
        DFS through the workflow DAG given be the result action:
        - set unique action names
        - detect input slots
        - (determine types of the input slots)
        :param result: the result action
        :param slots: List of the input slots of the workflow.
        :return: input slots
        """
        assert isinstance(result, _ActionBase)
        cls._result = result
        cls._slots = { slot.rank: slot for slot in slots }
        cls._actions = {}
        instance_names = {}

        def construct_previsit(action):
            # get instance name proposal
            if action.instance_name is None:
                name_base = action.action_name
                instance_names.setdefault(name_base, 1)
            else:
                name_base = action.instance_name

            # set unique instance name
            if name_base in instance_names:
                action.instance_name = "{}_{}".format(name_base, instance_names[name_base])
                instance_names[name_base] += 1
            else:
                action.instance_name = name_base
                instance_names[name_base] = 0

            # handle slots
            if isinstance(action, _Slot):
                assert action is cls._slots[action.rank]
            else:
                cls._actions[action.instance_name] = action

        cls._dfs(result,
                 previsit=construct_previsit,
                 edge_visit=lambda previous, action: previous.output_actions.append(action)
                 )




    def __init__(self, inputs=[], config=None, name=None):
        super().__init__(inputs, config, name)


    def evaluate(self, input):
        pass

    def _code(self, inputs, config=None):
        """ Representation of the workflow class instance within an outer workflow."""

        pass

    @classmethod
    def dependencies(cls):
        """
        :return: List of used actions (including workflows) and converters.
        """
        return [v.action_name for v in cls._actions.values()]

    @classmethod
    def code(cls):
        """
        Represent workflow by its source.
        :return: list of lines containing representation of the workflow as a decorated function.
        """



class Analysis:
    def __init__(self, workflow):
        self.workflow = workflow




def workflow(func):
    """
    Decorator to create a workflow class from the function.
    Create a derived Workflow class from a function that accepts the inputs returns an output action.
    :param func:
    :return:
    """
    action_name = func.__name__
    arg_spec = inspect.getargspec(func)
    arg_names = arg_spec.args
    slots = [_Slot(i, name) for i, name in enumerate(arg_names) ]
    output_action = func(*slots)
    attributes = {}
    new_workflow = type(action_name, (_WorkflowBase,), attributes)
    new_workflow._construct(output_action, slots)
    return new_workflow


def analysis(func):
    w = workflow(func)
    assert len(w._slots) == 0
    return Analysis(w)

class _Module:
    """
    Object representing a module (whole file) that can contain
    several worflow and converter definitions and possibly also a script itself.

    We  inspect __dict__ of the loaded module to find all definitions.
    The script must be a workflow function decorated with @analysis decorator.

    Only functions under the @converter, @workflow, and @action decorators are
    captured, remaining code is ignored.
    """
    def __init__(self, module_name):
        self.module = importlib.import_module(module_name)
        self.workflows = { k:v for k, v in self.module.__dict__.items() if isinstance(v, _WorkflowBase) }
        self.converters = { k:v for k, v in self.module.__dict__.items() if isinstance(v, _ConverterBase) }
        actions = {k: v for k, v in self.module.__dict__.items() if isinstance(v, _WorkflowBase)}
        assert len(actions) <= 1
        if actions:
            self.action = actions.values()[0]

    def code(self):
        pass

# class _FunctionAction
#     def __init__(self, ):
#         """
#         TODO: define constructor according to the function parameters.
#         """
# import inspect
# def action_from_function(func):
#     """
#     Returns the action class derived from the ActionBase with input parameters and types
#     determined automatically through the _Slot propagation mechanism and evauation method
#     determined by the function itself.
#     :param func:
#     :return:
#     """
#     action_name = func.__name__
#     inspect.getargvalues(func)
#     attributes = {
#         '__doc__' : "Action based on the function action_name.",
#         '__function' : func
#     }
#     action_class = type(action_name, (_FunctionAction,),  attributes)



"""
Object progression:
- Actions (implementation)

- Syntactic sugger classes
- ActionInstances - connection into WorkFlow
  This needs to be in close relation to previous since we want GUI - Python bidirectional conversions.
  
- Tasks - execution DAG
- Jobs
"""

