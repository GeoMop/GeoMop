
from typing import List, Any
from src.common.analysis import action_base as base
from src.common.analysis.action_instance import ActionInstance
"""
Implementation of the Workflow composed action.
- creating the 
"""




class Slot(ActionInstance):
    def __init__(self, slot_name=None):
        """
        Auxiliary action to connect to a named input slot of the workflow.
        :param slot_name:
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

class _ResultAction(base._ActionBase):
    """ Auxiliary result action."""
    def _evaluate(self, result: Any) -> None:
        pass

class Result(ActionInstance):
    """ Auxiliary result action instance, used to treat the result connecting in the consistnet way."""
    def __init__(self):
        super().__init__(_ResultAction(), "__result__")

    def code(self, module_dict):
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
    def edge_visit(previous, action, i_input):
        pass

    def run(self, root_action) -> bool:
        """
        Generic DFS for the action DAG.
        :param root_action: Starting vertex - the result action of the workflow
        :return: False in the case of found cycle.
        """
        action_closed = {}
        action_stack = [(root_action, 0)]
        while action_stack:
            action, i_input = action_stack.pop(-1)
            if i_input < len(action.arguments):
                action_stack.append((action, i_input + 1))
                input_action = action.arguments[i_input].value
                if input_action is None:
                    # TODO: possibly report missing input
                    continue
                # if not isinstance(input_action, ActionInstance):
                #     x=1
                assert isinstance(input_action, ActionInstance), (input_action.__class__, action.action_name, i_input)

                self.edge_visit(input_action, action, i_input)
                action_id = id(input_action)
                status = action_closed.get(action_id, None)
                if status is None:
                    # unvisited vertex
                    action_closed[action_id] = False
                    self.previsit(action)
                    action_stack.append((input_action, 0))
                elif not status:
                    # open vertex (cycle)
                    return False
            else:
                self.postvisit(action)
                action_closed[id(action)] = True
        return True


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
        self._result = Result()
        # Result subaction.
        self._slots = []
        # Definition of the workspace parameters ?
        self._actions = {}
        # Dict:  unique action instance name -> action instance.
        self._topology_sort = []
        # topoloicaly sorted actions

        self.update_parameters()

    @property
    def result(self):
        return self._result

    @property
    def slots(self):
        return self._slots

    def set_from_source(self, slots, output_type, output_action):
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

        is_dfs = DFS(postvisit=construct_postvisit)\
                    .run(self._result)
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
        Set argument 'i_arg' of the 'action' to 'input_action'.
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


    def set_result(self, result_type):
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



    """
    Necessary opeartions:

    
    - set_slot(i_slot, slot) - add/remove slots, removeing a slot moves order of others
    - set_action_input(action, i_arg, input_action) - performs also the update
      e.g. set_action_input(w.result, 0, input_action)
    
    Comments:
    - have auxiliary action Result (can not remove it)            
    - no need for add_action - just create one and connect it.
    - orphan actions are automatically removed, but these can be reconnected as long as 
      GUI keeps its own list of active actions
    - orphan actions are not saved to source
    """














