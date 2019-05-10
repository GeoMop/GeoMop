import os
import sys
import imp
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
    def __init__(self, inputs=[]):
        #assert hasattr(self, "__action_parameters")
        #self.__parameter_dict = { for i, (name, type) in self.__action_parameters}
        self.set_inputs(inputs)
        """ List of action instances connected to the input, predecessors in the workflow DAG. 
            Temporary solution. TODO: After Types are at least partially implemented we can use a Class instead of the 
            list in order to have named parameters, or even allow passing more parameters directly.
        """
        self.instance_name = None
        """ Unique ID within the workspace. Checked and updated during the workspace construction."""
        self._proper_instance_name = False
        """ Indicates the instance name provided by user."""
        self.output_actions = []
        """ Actions connected to the output. Set during the workflow construction."""


    @property
    def n_parameters(self):
        return self.__n_parameters



    @classmethod
    def action_name(cls):
        """
        Action name (not the instance name).
        :return:
        """
        return cls.__name__


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
        self._proper_instance_name = True
        return self

    def set_inputs(self, inputs):
        if self.n_parameters > -1:
            assert len(inputs) == self.n_parameters
        self._inputs = list(inputs)


    def _code(self):
        """
        Return a representation of the action instance.
        This is generic representation code that calls the constructor.

        Two

        :param inputs: Dictionary assigning strings to the Action's parameters.
        :param config: String used for configuration, call serialization of the configuration by default.
        :return: string (code to instantiate the action)
        """
        inputs = self._inputs
        inputs = ["{}".format(param.instance_name) for param in inputs]
        input_params = ", ".join(inputs)
        if self._proper_instance_name:
            name = ".name(\"{}\")".format(self.instance_name)
        else:
            name = ""
        code_line =  "{} = wf.{}({}){}".format(self.instance_name, self.action_name(), input_params, name)
        return code_line

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
        super().__init__()
        self.name(slot_name)
        self.rank = i_slot
        """ Slot rank. """
        self.type = None
        """ Slot type. None - slot not used. """


    def is_used(self):
        return bool(self.output_actions)

    def _code(self):
        return None



class _WorkflowBase(_ActionBase):
    """
    Every workflow is a class derived from this base.
    """

    @classmethod
    def _dfs(cls, root_action, previsit=None, postvisit=None, edge_visit=None):
        """
        Generic DFS for the action DAG.
        Not clear how to make non-recursive DFS with correct previsit and postvisit.
        :param root_action:
        :return:
        """
        action_ids = set()
        action_stack = [(root_action, 0)]
        while action_stack:
            action, i_input = action_stack.pop(-1)
            if i_input < len(action._inputs):
                action_stack.append((action, i_input + 1))
                input_action = action._inputs[i_input]
                assert isinstance(input_action, _ActionBase)
                if edge_visit:
                    edge_visit(input_action, action)
                    action_id = id(input_action)
                if action_id not in action_ids:
                    action_ids.add(action_id)
                    if previsit:
                        previsit(action)
                    action_stack.append((input_action, 0))
            else:
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
        cls._topology_sort = []
        instance_names = {}

        def construct_postvisit(action):
            # get instance name proposal
            if action.instance_name is None:
                name_base = action.action_name()
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
            cls._actions[action.instance_name] = action
            cls._topology_sort.append(action.instance_name)

        cls._dfs(result,
                 postvisit=construct_postvisit,
                 edge_visit=lambda previous, action: previous.output_actions.append(action))




    def __init__(self, inputs=[], config=None, name=None):
        super().__init__(inputs, config, name)

    def evaluate(self, input):
        pass

    def _code(self):
        """ Representation of the workflow class instance within an outer workflow."""

        pass

    @classmethod
    def dependencies(cls):
        """
        :return: List of used actions (including workflows) and converters.
        """
        return [v.action_name() for v in cls._actions.values()]

    @classmethod
    def code(cls):
        """
        Represent workflow by its source.
        :return: list of lines containing representation of the workflow as a decorated function.
        """
        params = [cls._slots[islot].instance_name for islot in range(len(cls._slots))]
        head = "def {}({}):".format(cls.action_name(), ", ".join(params))
        body = ["@wf.workflow", head]

        for iname in cls._topology_sort:
            action = cls._actions[iname]
            code = action._code()
            if code:
                body.append("    " + code)
        body.append("    return {}".format(cls._topology_sort[-1]))
        return "\n".join(body)





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
    attributes = dict(
        _result=None,   # Result subaction.
        _slots = {},    # Input slots of the workflow DAG.
        _actions = {},  # Dict:  unique action instance name -> action instance
        _is_analysis = False    # Marks the main workflow of the module
        )
    new_workflow = type(action_name, (_WorkflowBase,), attributes)
    new_workflow._construct(output_action, slots)
    return new_workflow



def analysis(func):
    """
    Decorator for the main analysis workflow of the module.
    """
    w = workflow(func)
    assert len(w._slots) == 0
    w.is_analysis = True
    return w


class _Module:
    """
    Object representing a module (whole file) that can contain
    several worflow and converter definitions and possibly also a script itself.

    We  inspect __dict__ of the loaded module to find all definitions.
    The script must be a workflow function decorated with @analysis decorator.

    Only functions under the @converter, @workflow, and @action decorators are
    captured, remaining code is ignored.
    """

    @staticmethod
    def create_from_source(name, source):
        """
        Create the _Module object from the source string 'source'.
        Named 'name'.
        """
        assert source, "Can not load empty source."
        new_module = imp.new_module(name)
        exec(source, new_module.__dict__)
        return _Module(new_module)

    @staticmethod
    def create_from_file(file_path):
        """
        Create a _Module form the given file path.
        """
        base = os.path.basename(file_path)
        base, ext = os.path.splitext(base)
        assert ext == ".py"
        with open(file_path, "r") as f:
            source = f.read()
        return _Module.create_from_source(name=base, source=source)

    @staticmethod
    def catch_object(name, object):
        """
        Predicate to identify Analysis definitions in the modlue dict.
        TODO: possibly catch without decorators
        Currently:
        - ignore underscored names
        - ignore non-classes
        - ignore classes not derived from _ActionBase
        - print all non-underscore ignored names
        """
        if not name or name[0] == '_':
            return False
        if inspect.isclass(object) and issubclass(object, _ActionBase):
            return True
        else:
            print('Ignored definition of: {}'.format(name))


    def __init__(self, module):
        """
        Constructor of the _Module wrapper.
        :param module: a python module object
        """
        self.module = module
        # Ref to wrapped python module object.
        self.definitions = {k:v for k, v in self.module.__dict__.items() if _Module.catch_object(k, v)}
        # List of analysis definition in the module (currently just defined workflows).
        self.analysis =  None
        # Instance of a workflow anotated by the decorator @analysis. Unique non-parametric workflow for running the analysis.
        analysis = [v for v in self.definitions.values() if v._is_analysis]
        assert len(analysis) <= 1
        if analysis:
            # make instance of the main workflow
            analysis = analysis.values()[0]
            self.analysis = analysis()
        else:
            self.analysis = None

    @property
    def name(self):
        return self.module.__name__

    def code(self):
        source = ["import common.analysis as wf"]
        for v in self.definitions.values():
            source.extend(["", ""])
            source.append(v.code())
        return "\n".join(source)

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

