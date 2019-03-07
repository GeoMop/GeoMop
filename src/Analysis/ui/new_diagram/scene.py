from PyQt5 import QtWidgets, QtCore, QtGui
from .root_action import RootAction
from .action import Action
from .connection import Connection
from .port import OutputPort
from .action_for_subactions import ActionForSubactions
from .graphics_data_model import ActionDataModel, ConnectionDataModel
import random


class ActionTypes:
    ACTION = 0
    CONNECTION = 1


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self):
        super(Scene, self).__init__()

        self.actions_for_subactions = []
        self.actions = []
        self.connections = []
        self.new_connection = None

        self.root_item = RootAction()
        self.addItem(self.root_item)

        self.new_action_pos = QtCore.QPoint()

        self.action_model = ActionDataModel()
        self.connection_model = ConnectionDataModel()
        self.action_model.dataChanged.connect(self.data_changed)
        self.connection_model.dataChanged.connect(self.data_changed)
        self.update_model = True

    @staticmethod
    def is_action(obj):
        """Return True if given object obj is an action."""
        if issubclass(type(obj), Action):
            return True
        else:
            return False

    def data_changed(self):
        self.update_model = True

    def update_scene(self):
        if self.update_model:
            self.update_model = False
            self.clear()
            self.connections.clear()
            self.actions.clear()
            if self.new_connection is not None:
                self.addItem(self.new_connection)
            for child in self.action_model.get_item().children():
                self.draw_action(child)

            for child in self.connection_model.get_item().children():
                self.draw_connection(child)

    def draw_action(self, item):
        if item.data(1) == ActionTypes.ACTION:
            self.actions.append(Action(item))
            self.addItem(self.actions[-1])

        for child in item.children():
            self.draw_item(child)

        self.update()

    def draw_connection(self, conn_data):
        port1 = self.get_action(conn_data.data(0)).get_port(False, conn_data.data(1))
        port2 = self.get_action(conn_data.data(2)).get_port(True, conn_data.data(3))
        self.connections.append(Connection(conn_data, port1, port2))
        port1.connections.append(self.connections[-1])
        port2.connections.append(self.connections[-1])
        self.addItem(self.connections[-1])
        self.update()

    def get_action(self, name):
        for action in self.actions:
            if action.name == name:
                return action

    def find_top_afs(self, pos):
        for item in self.items(pos):
            if issubclass(type(item), ActionForSubactions):
                return [item, item.mapFromScene(pos)]
        return [self.root_item, pos]

    def add_random_items(self):
        if not self.actions:
            self.new_action_pos = QtCore.QPoint(0, 0)
            self.add_action()
        for i in range(200):
            if i > 100:
                action = self.actions[random.randint(0,len(self.actions) - 1)]
                self.add_connection(action.in_ports[random.randint(0, len(action.in_ports) - 1)])
                action = self.actions[random.randint(0, len(self.actions) - 1)]
                self.add_connection(action.out_ports[random.randint(0, len(action.out_ports) - 1)])
            else:
                self.new_action_pos = QtCore.QPoint(random.randint(-800, 800), random.randint(-800, 800))
                self.add_action()
                self.update_scene()

    def mouseReleaseEvent(self, release_event):
        super(Scene, self).mouseReleaseEvent(release_event)

    # Modifying functions

    def move(self, action, new_pos):
        self.action_model.move(action, new_pos.x(), new_pos.y())
        self.update_model = False
        self.update()

    def add_action(self):
        """Create new action and add it to workspace."""
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.action_model.add_item(ActionTypes.ACTION, pos.x(), pos.y(), 50, 50)
        self.update_model = True
        #self.actions.append(Action(parent, pos))

    '''
    def add_while_loop(self):
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.actions.append(ActionForSubactions(parent, pos))
    '''

    def add_connection(self, port):
        """Create new connection from/to specified port and add it to workspace."""
        if self.new_connection is None:
            self.views()[0].setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.new_connection = Connection(None, port)
            self.addItem(self.new_connection)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable, False)
        else:
            self.views()[0].setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.new_connection.set_port2(port)
            port1 = self.new_connection.port1
            port2 = self.new_connection.port2
            self.connection_model.add_item(port1.parentItem().name, port1.index, port2.parentItem().name, port2.index)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable, True)
            self.new_connection = None
            self.update_model = True


    def delete_items(self):
        """Delete all selected items from workspace."""
        while self.selectedItems():
            """
            item = self.scene.selectedItems()[0]
            if self.is_action(item):
                for port in item.ports():
                    for conn in port.connections:
                        self.delete_connection(conn)
            """
            item = self.selectedItems()[0]
            if self.is_action(item):
                conn_to_delete = []
                for conn in self.connections:
                    for port in item.ports():
                        if conn.is_connected(port) and conn not in conn_to_delete:
                            conn_to_delete.append(conn)

                for conn in conn_to_delete:
                    try:
                        self.delete_connection(conn)
                    except:
                        print("Tried to delete connection again... probably...")
                self.delete_action(item)
            else:
                self.delete_connection(item)

    def delete_action(self, action):
        """Delete specified action from workspace."""
        self.action_model.removeRow(action.graphics_data_item.child_number())
        self.actions.remove(action)
        self.removeItem(action)

    def delete_connection(self, conn):
        self.connection_model.removeRow(conn.graphics_data_item.child_number())
        conn.port1.connections.remove(conn)
        conn.port2.connections.remove(conn)
        self.connections.remove(conn)
        self.removeItem(conn)
