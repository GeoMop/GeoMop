from .g_action import GAction


class GInputAction(GAction):
    def __init__(self, graphics_data_item, parent=None):
        super(GInputAction, self).__init__(graphics_data_item, parent)
        self.add_port(False, "Output Port")
