from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QGraphicsProxyWidget

from .composite_type_view import CompositeTypeView
from .g_input_action import GInputAction
from src.common.analysis.actions import Tuple
from .root_action import RootAction
from .g_action import GAction
from .g_connection import GConnection
from .gport import GOutputPort
from .action_for_subactions import GActionForSubactions
from .g_action_data_model import GActionDataModel, GActionData
import random
import math
import copy


class ActionTypes:
    ACTION = 0
    CONNECTION = 1


class Scene(QtWidgets.QGraphicsScene):
    def __init__(self, workflow, parent=None):
        super(Scene, self).__init__(parent)
        self.workflow = workflow
        self.actions = []
        self.new_connection = None

        self.root_item = RootAction()
        self.addItem(self.root_item)

        self.new_action_pos = QtCore.QPoint()

        self.action_model = GActionDataModel()
        self.action_model.dataChanged.connect(self.data_changed)
        self.update_model = True

        self.setSceneRect(QtCore.QRectF(QtCore.QPoint(-10000000, -10000000), QtCore.QPoint(10000000, 10000000)))

        self.initialize_workspace_from_workflow(workflow)

    def initialize_workspace_from_workflow(self, workflow):
        for action_name in workflow._actions:
            self._add_action(QPoint(0.0, 0.0), action_name)
            action = workflow._actions[action_name]

        for slot_name, slot in workflow._slots.items():
            self._add_action(QPoint(0.0, 0.0), slot.instance_name)

        self.update_scene()
        self.order_diagram()
        self.update_scene()
        self.parent().center_on_content = True

    @staticmethod
    def is_action(obj):
        """Return True if given object obj is an g_action."""
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
            self.actions.clear()
            self.root_item = RootAction()
            self.addItem(self.root_item)
            for child in self.action_model.get_item().children():
                self.draw_action(child)

            if self.new_connection is not None:
                self.addItem(self.new_connection)

            for action_name, action in self.workflow._actions.items():
                i = 0
                for other_action in action._inputs:
                    port1 = self.get_action(other_action.instance_name).out_ports[0]
                    port2 = self.get_action(action_name).in_ports[i]
                    port1.connections.append(GConnection(port1, port2))
                    port2.connections.append(port1.connections[-1])
                    self.addItem(port1.connections[-1])
                    i += 1

            self.update()

    def draw_action(self, item):
        action = self.workflow._actions.get(item.data(GActionData.NAME))
        if action is None:
            for rank, slot in self.workflow._slots.items():
                if slot.instance_name == item.data(GActionData.NAME):
                    action = slot
            self.actions.append(GInputAction(item, action, self.root_item))
        else:
            self.actions.append(GAction(item, action, self.root_item))

        for child in item.children():
            self.draw_action(child)

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
                self.move(item.g_data_item, None, prev_y)
            items = sorted(actions_by_levels[level], key=lambda item:item.x())
            middle = math.floor(len(items)/2)
            prev_item = items[middle]
            for i in range(middle + 1, len(items)):
                if items[i].pos().x() < prev_item.pos().x() + prev_item.width:
                    self.move(items[i].g_data_item, prev_item.pos().x() + prev_item.width + 10, None)
                prev_item = items[i]

            prev_item = items[middle]

            for i in range(middle - 1, -1, -1):
                if items[i].pos().x() + items[i].width > prev_item.pos().x():
                    self.move(items[i].g_data_item, prev_item.pos().x() - items[i].width - 10, None)
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

    def get_action(self, name: str) -> GAction:
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
                self.add_action(QtCore.QPoint(random.randint(-800, 800), random.randint(-800, 800)))
                self.update_scene()

    def mouseReleaseEvent(self, release_event):
        super(Scene, self).mouseReleaseEvent(release_event)

    def action_name_changed(self, action_data, new_name):
        if self.action_model.exists(new_name):
            return False
        self.action_model.name_changed(action_data,new_name)
        return True

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

    # Modifying functions

    def move(self, action, new_x, new_y):
        self.action_model.move(action, new_x, new_y)
        self.update_model = False
        self.update()

    def _add_action(self, new_action_pos, name=None):
        """Create new action and add it to workspace."""
        [parent, pos] = self.find_top_afs(new_action_pos)
        self.action_model.add_item(pos.x(), pos.y(), 50, 50, name)
        self.update_model = True

    def add_action(self, new_action_pos):
        action = Tuple()
        name = self.action_model.add_item(new_action_pos.x(), new_action_pos.y(), 50, 50, action.action_name)
        action.name(name)
        self.workflow._actions[name] = action


    '''
    def add_while_loop(self):
        [parent, pos] = self.find_top_afs(self.new_action_pos)
        self.actions.append(ActionForSubactions(parent, pos))
    '''

    def add_connection(self, port):
        """Create new connection from/to specified port and add it to workspace."""
        if self.new_connection is None:
            isinstance(port, GOutputPort)
            if isinstance(port, GOutputPort):
                self.enable_ports(False, False)
            else:
                self.enable_ports(True, False)
            self.views()[0].setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self.new_connection = GConnection(port)
            self.addItem(self.new_connection)
            self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable, False)
        else:
            if isinstance(port, GOutputPort):
                self.enable_ports(True, True)
            else:
                self.enable_ports(False, True)

            self.views()[0].setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            self.new_connection.set_port2(port)

            port1 = self.new_connection.port1
            port2 = self.new_connection.port2
            port1.connections.append(self.new_connection)
            port2.connections.append(self.new_connection)
            if self.is_graph_acyclic():
                action1 = port1.parentItem().w_data_item
                action2 = port2.parentItem().w_data_item
                action1.output_actions.append(action2)
                action2._inputs.append(action1)
                self.new_connection.setFlag(QtWidgets.QGraphicsPathItem.ItemIsSelectable, True)
                self.new_connection = None
                self.update_model = True
                """
                if port1.appending_port:
                    port1.appending_port = False

                if port2.appending_port:
                    port2.appending_port = False
                """
            else:
                msg = "Pipeline cannot be cyclic!"
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                            "Cyclic diagram", msg,
                                            QtWidgets.QMessageBox.Ok)
                msg.exec_()
                self.delete_connection(self.new_connection)
                self.new_connection = None

    def enable_ports(self, in_ports, enable):
        for action in self.actions:
            for port in action.in_ports if in_ports else action.out_ports:
                port.setEnabled(enable)

    def delete_items(self):
        """Delete all selected items from workspace."""
        while self.selectedItems():

            item = self.selectedItems()[0]
            if self.is_action(item):
                for port in item.ports():
                    while port.connections:
                        self.delete_connection(port.connections[0])

                self.delete_action(item)
            else:
                self.delete_connection(item)
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
                """

        self.update_model = True
        self.update()

    def delete_action(self, action):
        """Delete specified action from workspace."""
        self.action_model.removeRow(action.g_data_item.child_number())
        self.actions.remove(action)
        self.removeItem(action)
        self.workflow._actions.pop(action.name, None)

    def delete_connection(self, conn):
        action1 = conn.port1.parentItem().w_data_item
        action2 = conn.port2.parentItem().w_data_item
        action1.output_actions.remove(action2)
        action2._inputs.remove(action1)
        conn.port1.connections.remove(conn)
        conn.port2.connections.remove(conn)
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
