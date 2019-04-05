from PyQt5 import QtWidgets, QtCore, QtGui
from .root_action import RootAction
from .g_action import GAction
from .g_connection import GConnection
from .port import OutputPort
from .action_for_subactions import GActionForSubactions
from .graphics_data_model import ActionDataModel, ConnectionDataModel
import random
import math
import copy


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
        if issubclass(type(obj), GAction):
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
            self.root_item = RootAction()
            self.addItem(self.root_item)
            for child in self.action_model.get_item().children():
                self.draw_action(child)

            if self.new_connection is not None:
                self.addItem(self.new_connection)

            for child in self.connection_model.get_item().children():
                self.draw_connection(child)

    def draw_action(self, item):
        self.actions.append(GAction(item, self.root_item))
        #self.addItem(self.actions[-1])

        for child in item.children():
            self.draw_action(child)

        self.update()

    def draw_connection(self, conn_data):
        port1 = self.get_action(conn_data.data(0)).get_port(False, conn_data.data(1))
        port2 = self.get_action(conn_data.data(2)).get_port(True, conn_data.data(3))
        self.connections.append(GConnection(conn_data, port1, port2))
        port1.connections.append(self.connections[-1])
        port2.connections.append(self.connections[-1])
        self.addItem(self.connections[-1])
        self.update()

    def order_diagram(self):
        #todo: optimize by assigning levels when scanning from bottom actions
        queue = []
        for action in self.actions:
            if action.previous_actions():
                action.level = self.get_distance(action)
            else:
                queue.append(action)

        for action in queue:
            action.level = math.inf
            for next_action in action.next_actions():
                action.level = min(next_action.level - 1, action.level)
        self.reorganize_actions_by_levels()

    def reorganize_actions_by_levels(self):
        actions_by_levels = {}
        for action in self.actions:
            if action.level in actions_by_levels:
                actions_by_levels[action.level].append(action)
            else:
                actions_by_levels[action.level] = [action]
        levels = list(actions_by_levels.keys())
        levels.sort()
        base_item = actions_by_levels[levels[0]][-1]
        prev_y = base_item.y()
        max_height = base_item.height
        for level in levels:
            for item in actions_by_levels[level]:
                max_height = max(max_height, item.height)
            for item in actions_by_levels[level]:
                self.move(item.graphics_data_item, None, prev_y)
            items = sorted(actions_by_levels[level], key=lambda item:item.x())
            middle = math.floor(len(items)/2)
            prev_item = items[middle]
            for i in range(middle + 1, len(items)):
                if items[i].pos().x() < prev_item.pos().x() + prev_item.width:
                    self.move(items[i].graphics_data_item, prev_item.pos().x() + prev_item.width + 10, None)
                prev_item = items[i]

            prev_item = items[middle]

            for i in range(middle - 1, -1, -1):
                if items[i].pos().x() + items[i].width > prev_item.pos().x():
                    self.move(items[i].graphics_data_item, prev_item.pos().x() - items[i].width - 10, None)
                prev_item = items[i]

            prev_y = prev_y + max_height + 50

        self.update_model = True
        self.update()

    def get_distance(self, action):
        prev_actions = set(action.previous_actions())
        next_prev_actions = set()
        dist = 0
        while prev_actions:
            temp = prev_actions.pop()
            temp2 = temp.previous_actions()
            temp3 = set(temp.previous_actions())
            next_prev_actions = next_prev_actions.union(temp3)
            if not prev_actions:
                dist += 1
                prev_actions = next_prev_actions
                next_prev_actions = set()

        return dist

    def get_action(self, name):
        for action in self.actions:
            if action.name == name:
                return action

    def find_top_afs(self, pos):
        for item in self.items(pos):
            if issubclass(type(item), GActionForSubactions):
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

    def action_name_changed(self, action_data, new_name):
        if self.action_model.exists(new_name):
            return False
        self.connection_model.action_name_changed(action_data, new_name)
        self.action_model.name_changed(action_data,new_name)
        return True

    # Modifying functions

    def move(self, action, new_x, new_y):
        self.action_model.move(action, new_x, new_y)
        self.update_model = False
        self.update()

    def add_action(self):
        """Create new action and add it to workspace."""
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.action_model.add_item(pos.x(), pos.y(), 50, 50)
        self.update_model = True

    '''
    def add_while_loop(self):
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.actions.append(ActionForSubactions(parent, pos))
    '''

    def is_graph_acyclic(self):
        leaf_nodes = []
        processed_nodes = []
        acyclic_nodes = []
        for node in self.actions:
            if node.next_actions():
                pass
            else:
                leaf_nodes.append(node)

        for node in leaf_nodes:
            processed_nodes.append(node)
            acyclic_nodes.append(node)

            prev_actions = set(node.previous_actions())
            while prev_actions:
                curr = prev_actions.pop()
                if curr in acyclic_nodes:
                    continue
                else:
                    acyclic_nodes.append(curr)
                    if curr in processed_nodes:
                        return False
                    else:
                        processed_nodes.append(curr)
                        prev_actions = prev_actions.union(set(curr.previous_actions()))
        if len(acyclic_nodes) == len(self.actions):
            return True
        else:
            return False

    def add_connection(self, port):
        """Create new connection from/to specified port and add it to workspace."""
        if self.new_connection is None:
            isinstance(port, OutputPort)
            if isinstance(port, OutputPort):
                self.set_enable_ports(False, False)
            else:
                self.set_enable_ports(True, False)
            self.views()[0].setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.new_connection = GConnection(None, port)
            self.addItem(self.new_connection)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable, False)
        else:
            if isinstance(port, OutputPort):
                self.set_enable_ports(True, True)
            else:
                self.set_enable_ports(False, True)
            self.views()[0].setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.new_connection.set_port2(port)
            self.new_connection.port1.connections.append(self.new_connection)
            self.new_connection.port2.connections.append(self.new_connection)
            if self.is_graph_acyclic():
                port1 = self.new_connection.port1
                port2 = self.new_connection.port2
                self.connection_model.add_item(port1.parentItem().name, port1.index, port2.parentItem().name, port2.index)
                self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable, True)
                self.new_connection = None
                self.update_model = True
                if port1.appending_port:

                    port1.appending_port = False
                    #port1.parentItem().

                if port2.appending_port:
                    port2.appending_port = False
            else:
                msg = "Pipeline cannot be cyclic!"
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                            "Cyclic diagram", msg,
                                            QtWidgets.QMessageBox.Ok)
                msg.exec_()
                self.removeItem(self.new_connection)
                del self.new_connection.port1.connections[-1]
                del self.new_connection.port2.connections[-1]
                self.new_connection = None

    def set_enable_ports(self, in_ports, enable):
        for action in self.actions:
            for port in action.in_ports if in_ports else action.out_ports:
                port.setEnabled(enable)

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

        self.update_model = True
        self.update()

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

    def save_item(self, save_file, item, level=0):
        for child in item.children():
            save_file.write("\t"*level)
            for col in range(child.column_count()):
                save_file.write(str(child.data(col)) + ",")
            save_file.write("\n")
            self.save_item(save_file, child, level+1)

    def save_connection(self, index=QtCore.QModelIndex()):
        for child in self.connection_model.get_item().children():
            self.draw_connection(child)

    def load_item(self):
        pass
