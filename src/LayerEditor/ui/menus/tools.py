from PyQt5.QtWidgets import QMenu, QAction, QActionGroup
from ui.panels.diagram import OperatinState

class ToolsMenu(QMenu):
    """Menu with file actions."""

    def __init__(self, parent, diagram, title='&Settings'):
        """Initializes the class."""
        super(ToolsMenu, self).__init__(parent)
        self.setTitle(title)
        self._diagram = diagram
        self.parent = parent

        self._selmode_action = QAction('&Selection Mode', self)
        self._selmode_action.setCheckable(True)
        self._selmode_action.setStatusTip('On/off selection mode')
        self._selmode_action.triggered.connect(self._select_mode)
        self.addAction(self._selmode_action)
        self.addSeparator()
        
        self._operation_mode_group = QActionGroup(self, exclusive=True)
        self._operation_mode_group.triggered.connect(self._select_operation)

        self._point_op_action = QAction('&Point Operations', self)
        self._point_op_action.setCheckable(True)
        self._point_op_action.setChecked(True) 
        self._point_op_action.setData(OperatinState.point)
        self._operation_mode_group.addAction(self._point_op_action)
        self._point_op_action.setStatusTip('Set point operation mode')
        self.addAction(self._point_op_action)

        self._line_op_action = QAction('&Line Operations', self)
        self._line_op_action.setCheckable(True)
        self._point_op_action.setData(OperatinState.line)
        self._operation_mode_group.addAction(self._line_op_action)        
        self._line_op_action.setStatusTip('Set line operation mode')
        self.addAction(self._line_op_action)

    def _select_mode(self):
        """set diagram mode"""
        state = self._selmode_action.isChecked()
        self._diagram.set_select_mode(state)
        
    def _select_operation(self):
        """set diagram operation"""
        action = self._operation_mode_group.checkedAction()
        self._diagram.set_operation_state(action.data())
