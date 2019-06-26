
from typing import List, Any
from common.analysis import action_base as base
from common.analysis import task
from common.analysis import dfs
from common.analysis.action_instance import ActionInstance

"""
Implementation of the Workflow composed action.
- creating the 
"""




class Slot(ActionInstance):
    def __init__(self, slot_name):
        """
        Auxiliary action to connect to a named input slot of the workflow.
        :param slot_name: Slot name gives also name of appropriate Workflow's parameter.
        """
        super().__init__(base._ActionBase(), slot_name)
        self.arguments = []
        # self.rank = i_slot
        # """ Slot rank. """
        self.type = None
        """ Slot type. None - slot not used. """


    # def is_used(self):
    #     return bool(self.output_actions)


    def code(self, module_dict):
        return None

class _ResultAction(base._ListBase):
    """
     Auxiliary result action.
     Takes arbitrary number of inputs, at leas one input must be provided.
     Returns the first input, other inputs are used just for their side effects (using the Save action).

     Workflow decorator automatically connects all Save actions to the ignored result inputs.
    """
    def __init__(self):
        super().__init__()
        self.parameters = base.Parameters()
        self.parameters.append(base.ActionParameter(idx=0, name="result", type=Any, default=None))
        self.parameters.append(base.ActionParameter(idx=1, name=None, type=Any, default=self.parameters.no_default))


    def evaluate(self, inputs):
        return inputs[0]

class Result(ActionInstance):
    """ Auxiliary result action instance, used to treat the result connecting in the consistnet way."""
    def __init__(self):
        super().__init__(_ResultAction(), "__result__")

    def code(self, module_dict):
        return None




class _Workflow(base._ActionBase):
    """
    Represents a composed action.
    - Allows composition of the actions into a DAG
    - Is a child of _ActionBase, encapsulates its internal structure.
    """

    def __init__(self, name):
        """

        :param name:
        :param slots:
        :param result:
        :param params:
        :param output_type:
        """
        super().__init__(name)
        self.task_class = task.Composed
        self._result = Result()
        # Result subaction.
        self._slots = []
        # Definition of the workspace parameters ?
        self._actions = {}
        # Dict:  unique action instance name -> action instance.
        self._topology_sort = []
        # topologically sorted action instance names

        self.update_parameters()

    @property
    def result(self):
        return self._result

    @property
    def slots(self):
        return self._slots

    def set_from_source(self, slots, output_type, output_action):
        """
        Used by the workflow decorator to setup the instance.
        """
        self._slots = slots
        self._result.set_single_input(0, output_action)
        self._result.action.output_type = output_type

        is_dfs = self.update()
        assert is_dfs
        self.update_parameters()


    def update(self):
        """
        DFS through the workflow DAG given be the result action:
        - expand data to data actions
        - set unique action names
        - detect input slots
        - (determine types of the input slots)
        :param result: the result action
        :param slots: List of the input slots of the workflow.
        :return: True in the case of sucessfull update, False - detected cycle
        """
        actions = {}
        topology_sort = []
        instance_names = {}
        # clear output_actions
        for action in self._actions.values():
            action.output_actions = []

        def construct_postvisit(action):
            # get instance name proposal
            if action.name is None:
                name_base = action.action_name
                instance_names.setdefault(name_base, 1)
            else:
                name_base = action.name

            # set unique instance name
            if name_base in instance_names:
                action.name = "{}_{}".format(name_base, instance_names[name_base])
                instance_names[name_base] += 1
            else:
                action.name = name_base
                instance_names[name_base] = 0

            # handle slots
            #if isinstance(action, Slot):
            #    assert action is self._slots[action.rank]
            actions[action.name] = action
            topology_sort.append(action.name)

        # def edge_visit(previous, action, i_arg):
        #     return previous.output_actions.append((action, i_arg))

        is_dfs = dfs.DFS(neighbours=lambda action: (arg.value for arg in action.arguments),
                         postvisit=construct_postvisit).run([self._result])
        if not is_dfs:
            return False

        self._actions = actions
        self._topology_sort = topology_sort
        # set backlinks
        for action in self._actions.values():
            for i_arg, arg in enumerate(action.arguments):
                if arg.value is not None:
                    arg.value.output_actions.append((action, i_arg))
        return True

    # def evaluate(self, input):
    #     pass

    #def _code(self):
    #    """ Representation of the workflow class instance within an outer workflow."""
    #
    #    pass


    def dependencies(self):
        """
        :return: List of used actions (including workflows) and converters.
        """
        return [v.action_name() for v in self._actions.values()]

    
    def code_of_definition(self, module_name_dict):
        """
        Represent workflow by its source.
        :return: list of lines containing representation of the workflow as a decorated function.
        """
        decorator = 'analysis' if self.is_analysis else 'workflow'
        params = [base._VAR_]
        params.extend([self._slots[islot].name for islot in range(len(self._slots))])
        head = "def {}({}):".format(self.name, ", ".join(params))
        body = ["@{base_module}.{decorator}".format(base_module='wf', decorator=decorator), head]

        for iname in self._topology_sort:
            action_instance = self._actions[iname]
            code = action_instance.code(module_name_dict)
            if code:    # skip slots
                body.append("    " + code)
        assert len(self._result.arguments) > 0
        result_action = self._result.arguments[0].value
        body.append("    return {}".format(result_action.name))
        return "\n".join(body)


    def move_slot(self, from_pos, to_pos):
        """
        Move the slot at position 'from_pos' to the position 'to_pos'.
        Slots in between are shifted
        """
        assert 0 <= from_pos < len(self._slots)
        assert 0 <= to_pos < len(self._slots)
        from_slot = self._slots[from_pos]
        direction = 1 if to_pos > from_pos else -1
        for i in range(from_pos, to_pos, direction):
            self._slots[i] = self._slots[i + direction]
        self._slots[to_pos] = from_slot
        self.update_parameters()


    def insert_slot(self, i_slot:int , slot: Slot) -> None:
        """
        Insert a new slot on i_th position shifting the slot on i-th position and remaining to the right.
        Change of the name
        """
        assert 0 <= i_slot < len(self._slots) + 1
        self._slots.insert(i_slot, slot)
        self.update_parameters()


    def remove_slot(self, i_slot:int) -> None:
        """
        Disconnect and remove the i-th slot.
        """
        for dep_action, i_arg in self._slots[i_slot].output_actions:
            self.set_action_input(dep_action, i_arg, None)
        self._slots.pop(i_slot)
        self.update_parameters()


    def set_action_input(self, action: ActionInstance, i_arg:int, input_action: ActionInstance) -> bool:
        """
        Set argument 'i_arg' of the 'action' to the 'input_action'.

        E.g. wf.set_action_input(list_1, 0, slot_a)
        The result of the workflow is an action that takes arbitrary number of arguments but




        """
        if i_arg < len(action.arguments):
            orig_input = action.arguments[i_arg]
        else:
            orig_input = None
        action.set_single_input(i_arg, input_action)
        is_dfs = self.update()
        if not is_dfs:
            action.set_single_input(i_arg, orig_input)
            return False
        return True

        # # update back references: output_actions
        # action_arg = (action, i_arg)
        # if input_action is not None:
        #     input_action.output_actions.append(action_arg)
        # if orig_input is not None:
        #     orig_input.output_actions = [aa  for aa in orig_input.output_actions if aa != action_arg]


    def set_result_type(self, result_type):
        """
        TOOD: Test after introduction of typing.
        :param result_type:
        :return:
        """
        self.result.output_type = result_type


    def update_parameters(self):
        """
        Update outer interface: parameters and result_type according to slots and result actions.
        TODO: Check and set types.
        """
        self.parameters = base.Parameters()
        for i_param, slot in enumerate(self._slots):
            slot_expected_types = [a.arguments[i_arg].parameter.type  for a, i_arg in slot.output_actions]
            common_type = None #types.closest_common_ancestor(slot_expected_types)
            p = base.ActionParameter(i_param, slot.name, common_type)
            self.parameters.append(p)


    def expand(self, inputs):
        """
        Expansion of the composed task with given data inputs (possibly None if not evaluated yet).
        :param inputs: List[Task]
        :return: None if can not be expanded yet, otherwise return dict mapping action instance names to the created tasks.
        In particular slots are named ('__slot__', i) and result task have name '__result__'
        The composed task is then responsible for replacement of the slots by the input tasks and the result by the the composed task itself.
        """
        childs = {}
        assert len(self._slots) == len(inputs)
        # TODO: fix connection of slots to inputs
        for slot, input in zip(self._slots, inputs):
            childs[slot.name] = input
        for action_instance_name in self._topology_sort:
            if action_instance_name not in childs:
                action_instance = self._actions[action_instance_name]
                arg_tasks = [childs[arg.value.name] for arg in action_instance.arguments]
                childs[action_instance.name] = action_instance.action.task_class(action_instance.action, arg_tasks)
        return childs















