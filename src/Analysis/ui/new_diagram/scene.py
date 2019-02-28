from PyQt5 import QtWidgets, QtCore, QtGui
from .root_action import RootAction
from .action import Action
from .connection import Connection
from .action_for_subactions import ActionForSubactions
from .tree_model import TreeModel
import random

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

    @staticmethod
    def is_action(obj):
        """Return True if given object obj is an action."""
        if issubclass(type(obj), Action):
            return True
        else:
            return False

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
                self.add_connection(action.ports()[random.randint(0, len(action.ports()) - 1)])
                action = self.actions[random.randint(0, len(self.actions) - 1)]
                self.add_connection(action.ports()[random.randint(0, len(action.ports()) - 1)])
            else:
                action = self.actions[random.randint(0, len(self.actions) - 1)]
                self.new_action_pos = action.pos() + QtCore.QPoint(random.randint(-800, 800), random.randint(-800, 800))
                self.add_action()

    def add_action(self):
        """Create new action and add it to workspace."""
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.actions.append(Action(parent, pos))

    def add_while_loop(self):
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.actions.append(ActionForSubactions(parent, pos))

    def add_connection(self, port):
        """Create new connection from/to specified port and add it to workspace."""
        if self.new_connection is None:
            self.new_connection = Connection(port)
            self.addItem(self.new_connection)
            port.connections.append(self.new_connection)
        else:
            self.new_connection.set_port2(port)
            port.connections.append(self.new_connection)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable)
            self.connections.append(self.new_connection)
            self.new_connection = None

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
        self.actions.remove(action)
        self.removeItem(action)

    def delete_connection(self, conn):
        conn.port1.connections.remove(conn)
        conn.port2.connections.remove(conn)
        self.connections.remove(conn)
        self.removeItem(conn)
