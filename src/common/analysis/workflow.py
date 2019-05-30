
import inspect
import indexed
import attr
from common.analysis import dummy, types
from common.analysis import action_base as base

"""
"""


class _Slot(base._ActionBase):
    def __init__(self, i_slot, slot_name=None):
        """
        Auxiliary action to connect to a named input slot of the workflow.
        :param slot_name:
        """
        super().__init__()
        self.instance_name = slot_name
        self.rank = i_slot
        """ Slot rank. """
        self.type = None
        """ Slot type. None - slot not used. """


    def is_used(self):
        return bool(self.output_actions)

    def _code(self):
        return None


class DFS:
    def __init__(self, previsit=None, postvisit=None, edge_visit=None):
        self.previsit = previsit or self.previsit
        self.postvisit = postvisit or self.postvisit
        self.edge_visit = edge_visit or self.edge_visit

    @staticmethod
    def previsit(action):
        pass

    @staticmethod
    def postvisit(action):
        pass

    @staticmethod
    def edge_visti(previous, action, i_input):
        pass

    def run(self, root_action):
        """
        Generic DFS for the action DAG.
        :param previsit: previsit(action)
        :param postvisit: postvisit(action)
        :param edge_visit: edge_visit(outcomming_action, incomming_action, incomming_input_index)
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
                assert isinstance(input_action, base._ActionBase), (input_action.__class__, action, i_input)

                self.edge_visit(input_action, action, i_input)
                action_id = id(input_action)
                if action_id not in action_ids:
                    action_ids.add(action_id)
                    self.previsit(action)
                    action_stack.append((input_action, 0))
            else:
                self.postvisit(action)


class _WorkflowBase(base._ActionBase):
    """
    Every workflow is a class derived from this base.
    """


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

        def edge_visit(previous, action, i_arg):
            return previous.output_actions.append((action, i_arg))

        DFS(postvisit=construct_postvisit, edge_visit=edge_visit).run(result)
        cls.parameters = indexed.IndexedOrderedDict()
        for i_param, slot in enumerate(cls._slots):
            slot_expected_types = [a.arguments[i_arg].parameter.type  for a, i_arg in slot.output_actions]
            common_type = None #types.closest_common_ancestor(slot_expected_types)
            p = base.ActionParameter(i_param, slot.instance_name, common_type)
            cls.parameters[slot.instance_name] = p


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def evaluate(self, input):
        pass

    #def _code(self):
    #    """ Representation of the workflow class instance within an outer workflow."""
    #
    #    pass

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
        params = [base._VAR_]
        params.extend([cls._slots[islot].instance_name for islot in range(len(cls._slots))])
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
    """
    Helper class to store local variables of the workflow and use
    their names as instance names for the assigned actions, i.e.
    variables.x = action_y(...)
    will set the instance name of 'action_y' to 'x'. This allows to
    use 'x' as the variable name in subsequent code generation. Otherwise
    a Python variable name is not accessible at runtime.
    """
    def __setattr__(self, key, value):
        value = base._wrap_action(value)
        value = value.set_name(key)
        self.__dict__[key] = value


def workflow(func):
    """
    Decorator to crate a Workflow class from a function.
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
    dummies = [dummy.Dummy(slot) for slot in slots]
    func_args.extend(dummies)
    output_action = func(*func_args)
    attributes = dict(
        _result=None,   # Result subaction.
        _vars = vars,   # Temporary variables. TODO: possibly not necessary to store
        _slots = slots,
        _actions = {},  # Dict:  unique action instance name -> action instance.
                        # TODO: possibly better to save topologically sorted list of actions, e.g. in OrderedDict
        _topology_sort = []
        )
    new_workflow_class = type(workflow_name, (_WorkflowBase,), attributes)
    new_workflow_class._construct(output_action, slots)
    return dummy.public_action(new_workflow_class)






def analysis(func):
    """
    Decorator for the main analysis workflow of the module.
    """
    w = workflow(func)
    assert len(w.action_class._slots) == 0
    w.is_analysis = True
    return w


class ClassActionBase(base._ActionBase):
    """
    Dataclass action
    """
    def __init__(self):
        super().__init__()
        self._module = ""

    @classmethod
    def _evaluate(cls, **kwargs):
        return cls._data_class(**kwargs)

    @classmethod
    def code(cls):
        lines = ['@wf.Class']
        lines.append('class {}:'.format(cls.action_name()))
        for attribute in cls._data_class.__attrs_attrs__:
            type_str = attribute.type.__name__ if attribute.type else "Any"
            if attribute.default == attr.NOTHING:
                default = ""
            else:
                default = "={}".format(attribute.default)
            lines.append("  {}:{}{}".format(attribute.name, type_str, default))

        return "\n".join(lines)


def Class(data_class):
    """
    Decorator to add dunder methods using attr.
    Moreover dot access returns the converter.Get action instead of the value itself.
    This is necessary to catch it in the workflow decorator.
    """
    data_class = attr.s(data_class, auto_attribs=True)
    attributes = dict(
        _data_class = data_class
        )
    dataclass_action = type(data_class.__name__, (ClassActionBase,), attributes)
    dataclass_action._extract_input_type(func=data_class.__init__, skip_self=True)
    return dummy.public_action(dataclass_action)