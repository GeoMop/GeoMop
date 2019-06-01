import inspect
import indexed

from common.analysis import action_base as base
from common.analysis.action_instance import ActionInstance
"""
Implementation of the Workflow composed action.
- creating the 
"""




class _Slot(ActionInstance):
    def __init__(self, i_slot, slot_name=None):
        """
        Auxiliary action to connect to a named input slot of the workflow.
        :param slot_name:
        """
        super().__init__(base._ActionBase(), slot_name)
        self.arguments = []
        self.rank = i_slot
        """ Slot rank. """
        self.type = None
        """ Slot type. None - slot not used. """


    def is_used(self):
        return bool(self.output_actions)


    def code(self):
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
                # if not isinstance(input_action, ActionInstance):
                #     x=1
                assert isinstance(input_action, ActionInstance), (input_action.__class__, action.action_name, i_input)

                self.edge_visit(input_action, action, i_input)
                action_id = id(input_action)
                if action_id not in action_ids:
                    action_ids.add(action_id)
                    self.previsit(action)
                    action_stack.append((input_action, 0))
            else:
                self.postvisit(action)



class _Workflow(base._ActionBase):
    """
    Every workflow is a class derived from this base.
    """


    def __init__(self, name, vars, slots, result, params, output_type):
        super().__init__(name)
        self.parameters = params
        self.output_type = output_type
        #
        self._result = result
        # Result subaction.
        self._vars = vars
        # Temporary variables. TODO: possibly not necessary to store
        self._slots = slots
        # Definition of the workspace parameters ?
        self._actions = {}
        # Dict:  unique action instance name -> action instance.
        self._topology_sort = []
        # topoloicaly sorted actions
        self._construct()


    def _construct(self):
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
        instance_names = {}

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
            if isinstance(action, _Slot):
                assert action is self._slots[action.rank]
            self._actions[action.name] = action
            self._topology_sort.append(action.name)

        def edge_visit(previous, action, i_arg):
            return previous.output_actions.append((action, i_arg))

        DFS(postvisit=construct_postvisit, edge_visit=edge_visit).run(self._result)
        self.parameters = base.Parameters()
        for i_param, slot in enumerate(self._slots):
            slot_expected_types = [a.arguments[i_arg].parameter.type  for a, i_arg in slot.output_actions]
            common_type = None #types.closest_common_ancestor(slot_expected_types)
            p = base.ActionParameter(i_param, slot.name, common_type)
            self.parameters.append(p)


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

    
    def code_of_definition(self):
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
            code = action_instance.code()
            if code:    # skip slots
                body.append("    " + code)
        body.append("    return {}".format(self._topology_sort[-1]))
        return "\n".join(body)

















