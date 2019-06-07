from .g_action import GAction


class OutputGAction(GAction):
    def __init__(self, graphics_data_item, parent=None):
        super(OutputGAction, self).__init__(graphics_data_item, parent)
        self.add_port(True, "Input Port")
