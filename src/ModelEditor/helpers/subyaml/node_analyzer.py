from enum import Enum
from helpers.subyaml.line_analyzer import LineAnalyzer
from data import Position, CompositeNode


class NodeAnalyzer:
    """
    Anayze partial yaml node

    Description: This quick party text analyzing contains node
    specific function.
    """
    
    def __init__(self, lines, node):
        self._lines = lines
        """Array of yaml doc lines"""
        self._node = node
        """analyzed node"""
        
    def get_node_structure_type(self):
        """Get node structure type :class:`helpers.subyaml.node_analyzer.NodeStructureType`"""
        if isinstance(self._node,  CompositeNode):
            if self._node.explicit_keys:
                json_start = self.get_start_inner_json_tag()
                if json_start is not None:
                     return NodeStructureType.json_array
                return NodeStructureType.array
            else:
                json_start = self.get_start_inner_json_tag()
                if json_start is not None:
                    return NodeStructureType.json_dict
                return NodeStructureType.dict
        return NodeStructureType.scalar
        
    def get_start_inner_json_tag(self):
        """Find start possition of inner json"""
        start_pos = self.get_node_key_end()
        end_pos = self._node.span.start
        if isinstance(self._node,  CompositeNode) and \
            len(self._node.children) > 0:
            end_pos = self._node.children[0].start
        if start_pos is not None and end_pos is not None and \
           start_pos.line <= end_pos.line:
            for i in range(start_pos.line, end_pos.line+1):
                if i>len(self._lines):
                    break
                start=0
                if start_pos.line == i:
                   start = start_pos.column - 1
                end = len(self._lines[i-1])
                if end_pos.line == i:
                    end = end_pos.column - 1
                for char in ["{","[" ]:
                    pos = LineAnalyzer.get_separator(self._lines[i-1],char, start, end)
                    if pos != -1:
                        return Position(i, pos+1)
        return None    
        
    def get_end_inner_json_tag(self):
        """Find start possition of inner json"""
        start_pos = self._node.span.start
        end_pos = self._node.span.end
        if isinstance(self._node,  CompositeNode) and \
            len(self._node.children) > 0:
            start_pos = self._node.children[len(self._node.children)-1].end
        if start_pos is not None and end_pos is not None and \
           start_pos.line <= end_pos.line:
            for i in range(start_pos.line, end_pos.line+1):
                if i>len(self._lines):
                    break
                start=0
                if start_pos.line == i:
                   start = start_pos.column - 1
                end = len(self._lines[i-1])
                if end_pos.line == i:
                    end = end_pos.column - 1
                for char in ["}","]" ]:
                    pos = LineAnalyzer.get_separator(self._lines[i-1],char, start, end)
                    if pos != -1:
                        return Position(i, pos+1)
        return None
    
    def get_node_key_end(self):
        """Get possition after key (or tag, anchor, ... if is not None)"""
        start_pos = self._node.start
        if self._node.key is not None and self._node.key.span is not None:
            start_pos = self._node.key.span.end
            dist = -1
            i = start_pos.line-1
            if start_pos.column > len(self._lines[i]):
                i =+ 1
                if i >  self._node.end.line-1:
                    return start_pos
                line =  self._lines[i]
            else:
                line =  self._lines[i][start_pos.column-1:]   
            while dist == -1: 
                is_dist, dist =  LineAnalyzer.get_after_key_area(line)
                if is_dist:
                    if dist != -1:
                        return Position(i+1, dist)
                    else:
                        i += 1
                        if i >  self._node.end.line-1:
                            return self._node.end
                        line =  self._lines[i]
                else:
                    return Position(i+1, 1)
        return start_pos

class NodeStructureType(Enum):
    scalar = 1
    array = 2
    dict = 3
    json_array = 4
    json_dict = 5
