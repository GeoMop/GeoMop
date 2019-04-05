from .action import Action


class OutputAction(Action):
    def __init__(self, graphics_data_item, parent=None):
        super(OutputAction, self).__init__(graphics_data_item, parent)
        self.add_port(True, "Input Port")
