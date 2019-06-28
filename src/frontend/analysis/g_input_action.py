from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPainterPath

from .g_action_background import ActionStatus
from .g_workflow_input_port import GWorkflowInputPort
from .g_action import GAction


class GInputAction(GAction):
    def __init__(self, g_data_item, w_data_item, parent=None):
        super(GInputAction, self).__init__(g_data_item, w_data_item, parent)

    def _add_ports(self, n_ports):
        self.add_g_port(False, "Output Port")
        self.in_ports.append(GWorkflowInputPort(parent=self))

