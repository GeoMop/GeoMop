

class WorkflowInterface:
    def __init__(self, workflow):
        if workflow is None:
            raise ValueError
        self.workflow = workflow

    def get_actions(self):
        pass

    def get_slots(self):
        pass

    def get_


