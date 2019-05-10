from src.common.analysis.base import _WorkflowBase


class WorkflowInterface:
    def __init__(self, workflow):
        if workflow is None:
            raise ValueError
        self.workflow = _WorkflowBase.__class__
        self.workflow = workflow

    def get_actions(self):
        return self.workflow._actions

    def get_slots(self):
        return self.workflow._slots

    def get_result_action(self):
        return self.workflow._result


