"""Structure analyzer.

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""

from gm_base.geomop_util import Position, Span
from gm_base.model_data import DataNode, Notification

from .node_analyzer import NodeAnalyzer
from .line_analyzer import LineAnalyzer


class StructureAnalyzer:
    """
    Anayze yaml file for find specific attribute, for examle json structure
    """
    def __init__(self):
        """init"""
        pass

    @staticmethod
    def _get_array_separator(lines, start_pos, end_pos):
        """get array separator"""
        if start_pos is not None and end_pos is not None and \
           start_pos.line <= end_pos.line:
            for i in range(start_pos.line, end_pos.line+1):
                if i>len(lines):
                    break
                start=0
                if start_pos.line == i:
                   start = start_pos.column - 1
                end = len(lines[i-1])
                if end_pos.line == i:
                    end = end_pos.column - 1
                pos = LineAnalyzer.get_separator(lines[i-1],"-", start, end)
                if pos != -1:
                    return Position(i, pos+1)
        return None

    @staticmethod
    def _get_json_separator(lines, start_pos, end_pos):
        """get array separator"""
        if start_pos is not None and end_pos is not None and \
           start_pos.line <= end_pos.line:
            for i in range(start_pos.line, end_pos.line+1):
                if i > len(lines):
                    break
                start = 0
                if start_pos.line == i:
                    start = start_pos.column - 1
                end = len(lines[i-1])
                if end_pos.line == i:
                    end = end_pos.column - 1
                for char in ["{", "[", ",", "}", "]"]:
                    pos = LineAnalyzer.get_separator(lines[i-1], char, start, end)
                    if pos != -1:
                        return Position(i, pos+1)
        return None

    @classmethod
    def add_node_info(cls, doc, root, notification_handler):
        """Add border information about nodes"""
        lines = doc.splitlines()
        if root.implementation != DataNode.Implementation.scalar:
            cls._analyze_node(lines, root, notification_handler)

    @classmethod
    def _analyze_node(cls, lines, node, notification_handler):
        """Node analysis is performed recursively"""
        na = NodeAnalyzer(lines, node)
        node_type = na. get_node_structure_type()
        if node_type == DataNode.StructureType.json_array or \
                node_type == DataNode.StructureType.json_dict:
            cls._split_children(lines, node, cls._get_json_separator)
            if (len(node.children) > 0 and
                    node.children[0].delimiters is not None and
                    node.children[0].delimiters.start is not None and
                    node.children[len(node.children) - 1].delimiters is not None and
                    node.children[len(node.children) - 1].delimiters.end is not None and
                    node.children[0].delimiters.start.line <
                    node.children[len(node.children) - 1].delimiters.end.line):
                notification = Notification.from_name('MultiLineFlow')
                notification.span = node.span
                notification_handler.report(notification)
        elif node_type == DataNode.StructureType.array:
            cls._split_children(lines, node, cls._get_array_separator, False)
        for child in node.children:
            if child.implementation != DataNode.Implementation.scalar:
                cls._analyze_node(lines, child, notification_handler)

    @classmethod
    def _split_children(cls, lines, node, func, is_flow=True):
        """Find and write separators (borders) positions between nodes"""
        if len(node.children) > 0:
            na = NodeAnalyzer(lines, node)
            start_pos = func(lines, na.get_node_key_end(), node.children[0].start)
            if len(node.children) == 1:
                if is_flow:
                    end_pos = func(lines, node.children[0].end, node.end)
                else:
                    end_pos = node.children[0].end
            else:
                end_pos = func(lines, node.children[0].end,  node.children[1].start)
            node.children[0].is_flow = is_flow
            node.children[0].delimiters = Span(start_pos, end_pos)
        for i in range(1, len(node.children)-1):
            start_pos = end_pos
            end_pos = func(lines, node.children[i].end,  node.children[i+1].start)
            node.children[i].is_flow = is_flow
            node.children[i].delimiters = Span(start_pos, end_pos)
        if len(node.children) > 1:
            start_pos = end_pos
            if is_flow:
                end_pos = func(lines, node.children[len(node.children)-1].end,  node.end)
            else:
                end_pos = node.children[len(node.children)-1].end
            node.children[len(node.children)-1].is_flow = is_flow
            node.children[len(node.children)-1].delimiters = Span(start_pos, end_pos)
            
    @staticmethod
    def is_edit_parent_array(node):
        """Return whether parent node is array. If parent was created
        by autoconversion, is tested parent.parent

        :param Node node: test node
        :return: True when parent is array
        :rtype: bool
        """
        test_node = node.parent
        test_child_node = node
        while test_node.parent is not None and \
            test_child_node.origin != DataNode.Origin.structure:
            test_child_node = test_node
            test_node = test_node.parent
        while test_node.parent is not None and \
            test_node.origin != DataNode.Origin.structure:
            test_node = test_node.parent
        if test_node.parent is None:
            return False
        return test_node.implementation == DataNode.Implementation.sequence            
