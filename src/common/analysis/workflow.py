from common.analysis import action_base as base
import inspect

class _Slot(base._ActionBase):
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



class _WorkflowBase(base._ActionBase):
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
            if i_input < len(action.arguments):
                action_stack.append((action, i_input + 1))
                input_action = action.arguments[i_input].value
                assert isinstance(input_action, base._ActionBase)
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
        - expand data to data actions
        - set unique action names
        - detect input slots
        - (determine types of the input slots)
        :param result: the result action
        :param slots: List of the input slots of the workflow.
        :return: input slots
        """
        result = base._wrap_action(result)
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




    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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



class _Variables:
    def __setattr__(self, key, value):
        value = base._wrap_action(value)
        value = value.name(key)
        self.__dict__[key] = value



def workflow(func):
    """
    Decorator to create a workflow class from the function.
    Create a derived Workflow class from a function that accepts the inputs returns an output action.
    :param func:
    :return:
    """
    workflow_name = func.__name__
    workflow_signature = inspect.signature(func)
    parameters = workflow_signature.parameters
    param_names = [param.name for param in parameters.values()]
    func_args = []
    if param_names[0] == 'self':
        func_args.append(_Variables())
        param_names = param_names[1:]

    slots = [_Slot(i, name) for i, name in enumerate(param_names) ]
    func_args.extend(slots)
    output_action = func(*func_args)
    attributes = dict(
        _result=None,   # Result subaction.
        _vars = vars,   # Temporary variables.
        _slots = {},    # Input slots of the workflow DAG.
        _actions = {},  # Dict:  unique action instance name -> action instance
        _is_analysis = False    # Marks the main workflow of the module
        )
    new_workflow_class = type(workflow_name, (_WorkflowBase,), attributes)
    new_workflow_class._construct(output_action, slots)
    return new_workflow_class




