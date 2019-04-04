from .action import Action


class InputAction(Action):
    def __init__(self, graphics_data_item, parent=None):
        super(InputAction, self).__init__(graphics_data_item, parent)
        self._add_port(False, "Output Port")
