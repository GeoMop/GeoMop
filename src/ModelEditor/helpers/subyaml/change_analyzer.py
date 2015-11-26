"""Helper for yaml text editor

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""
import re
import copy

from util import KeyType, PosType

from .line_analyzer import LineAnalyzer


class ChangeAnalyzer:
    """
    Analyzes partial yaml text for change character report

    Description: This quick partial text analysis is used to decide whether more time consuming
    text parsing is necessary.
    
    This class works with dirty data, that is not refreshed in data node structure.
    """

    def __init__(self, cursor_line, cursor_index, area):
        """Initialize the class.

        :param int cursor_line: position of the cursor (line)
        :param int cursor_index: position of the cursor (column)
        :param list<str> area: list of lines in the surrounding area
        """
        self._area = copy.deepcopy(area)
        for line in range(0, len(self._area)):
            if self._area[line][-1:] == "\n":
                self._area[line] = self._area[line][0:-1]
        self._line = cursor_line
        self._index = cursor_index
        if len(self._area[self._line]) <= self._index:
            self._index = len(self._area[self._line]) - 1

    def get_pos_type(self):
        """Recognize the part of the data structure that is pointed to by a current cursor.

        There are a couple of reasons to call this function.

        First, it can recognize whether reload is effective??? In this case, the function
        returns ``in_inner``. It may be necessary to still check if cursor is above
        child node. ???

        Second, the function is useful to figure out which part of the data node structure
        has been changed. If there are multiple changes in one data node structure, a reload
        is needed.

        :return: position indicator of the part of the structure below cursor

           - ``in_key`` for key, tag, reference or anchor, but only if this belong to set data node
           - ``comment`` for cursor above comment
           - ``in_inner`` for child :py:class:`DataNode` structure
           - ``in_value`` for scalar node value or structure between child nodes
        :rtype: PosType
        """    # TODO: when is in_inner returned? how is it related to "reload is effective"?
        is_key = False
        json_list = 0
        inner = False
        i = 0
        while i < len(self._area):
            # key
            index = LineAnalyzer.get_char_poss(self._area[i], ":")
            if not is_key:
                # first key
                if index > -1:
                    nline, nindex = self._get_key_area(i)
                    if self._line < nline or (self._line == nline and self._index < nindex):
                        return PosType.in_key
                    if i != nline:
                        i = nline
                        index = nindex
                is_key = True
                if LineAnalyzer.get_char_poss(self._area[i][index+1:], ":") > -1:
                    inner = True
            else:
                if index > -1:
                    inner = True
            # inner
            if not inner and i > 0:
                start = re.match(r'^\s*-\s+\S', self._area[i])
                if start:
                    inner = True
            # multiline - not resolve
            index = self._area[i].find("|")
            if index == -1:
                index = self._area[i].find(">")
            if index == len(self._area[i])-1:
                if inner:
                    return PosType.in_inner
                return PosType.in_value
            # comment
            index = self._area[i].find("#")
            if index > -1:
                if self._line == i and self._index > index:
                    return PosType.comment
            # json list +
            index = self._area[i].find("[")
            while index > -1:
                json_list += 1
                index = self._area[i].find("[", index+1)
            index = self._area[i].find("{")
            while index > -1:
                json_list += 1
                index = self._area[i].find("{", index+1)
            # json
            if i == self._line:
                if json_list > 0:
                    if self._area[i][self._index] in [" ", ",", "[", "]", "{", "}"]:
                        return PosType.in_value
                    return PosType.in_inner
            index = self._area[i].find("]")
            # json-
            while index > -1:
                json_list -= 1
                index = self._area[i].find("]", index+1)
            index = self._area[i].find("}")
            while index > -1:
                json_list -= 1
                index = self._area[i].find("}", index+1)
            # inner process
            if inner and i == self._line:
                start = re.search(r'^\s*-\s\S', self._area[i])
                if not start:
                    start = re.search(r'^\s*\S', self._area[i])
                if not start:
                    return PosType.in_value
                if len(start.group(0)) > self._index:
                    return PosType.in_value
                return PosType.in_inner
            i += 1
        return PosType.in_value

    def _get_key_area(self, line):
        """get new line and index for init object"""
        i = line
        is_dist, dist = LineAnalyzer.get_key_area(self._area[i])
        if not is_dist:
            return line, 0
        if dist != -1:
            return i, dist-1
        while dist == -1:
            i += 1
            if i >= len(self._area):
                space_after = re.search(r'(.*\S)\s+$', self._area[i-1])
                if space_after is not None:
                    return i-1, space_after.end(1)
                return i, 0
            is_dist, dist = LineAnalyzer.get_after_key_area(self._area[i])
            if is_dist:
                if dist != -1:
                    return i, dist-1
            else:
                space_after = re.search(r'(.*\S)\s+$', self._area[i-1])
                if space_after is not None:
                    return i-1, space_after.end(1)
                return i, 0

    def get_key_pos_type(self):
        """Get more specific key type definition.

        When the ``get_pos_type`` method returns ``in_key``, more specific position may
        be acquired by this method.

        :return: specific position in key (like key, tag, anchor or reference)
        :rtype: KeyType
        """
        i = 0
        dist = 0
        type_ = KeyType.key

        next_line = False
        # skip key (if cursore is above key, next block is skipped and
        # default value is returned KeyType.key)
        while i <= self._line:
            line = LineAnalyzer.strip_comment(self._area[i])
            key = re.match(r'[^:]+:\s*$', line)
            if key is not None:
                if self._line == i:
                    return type_
                next_line = True
                break
            key = re.match(r'([^:]+:\s)', line)
            if key is not None:
                if self._line == i and self._index < key.end(1):
                    return type_
                line = line[key.end(1):]
                dist += key.end(1)
                break
            i += 1
        # recignise tags, anchors or refferences
        while i <= self._line:
            if next_line:
                i += 1
                if i > self._line:
                    return type_
                line = LineAnalyzer.strip_comment(self._area[i])
                if line.isspace() or len(line) == 0:
                    continue
                dist = 0
                next_line = False
            next_line = True
            for char in ['!', '&', r'<<: \*', r'\*']:
                index = line.find(char)
                if index > -1:
                    area = re.match(r'\s*(' + char + r'\S+\s*)$', line)
                    if area is not None:
                        # area is all line
                        if self._line == i:
                            return self. _get_type_from_char(char)
                        break
                    else:
                        area = re.match(r'\s*(' + char + r'\S+\s+)\S', line)
                        if area is not None:
                            if self._line == i and self._index < (area.end(1)+dist):
                                return self. _get_type_from_char(char)
                            line = line[area.end(1):]
                            dist += area.end(1)
                            type_ = self. _get_type_from_char(char)
                            next_line = False
                            break
        return type_

    @staticmethod
    def _get_type_from_char(char):
        """return key type from char"""
        if char == '!':
            return KeyType.tag
        elif char == '*':
            return KeyType.ref
        elif char == '<<: *':
            return KeyType.ref_a
        elif char == '&':
            return KeyType.anch
        else:
            return KeyType.key

    # TODO: move is_xxx_struct methods to LineAnalyzer?

    @staticmethod
    def is_basejson_struct(add):
        """Return if is in line json base structure for evaluation
        
        If line has new json structure added in json node, reload is needed
        """
        patterns = [
            r'\s*\S+,\s*',
            r'\s*,\S+\s*'
        ]
        for pat in patterns:
            area = re.search(pat, add)
            if area is not None:
                return True
        return False
        
    @staticmethod
    def is_fulljson_struct(add):
        """Return if is in line json base structure for evaluation
        
        If line has new json structure, reload is needed
        """
        patterns = [
            r'\[.+\]',
            r'\{.+\}'
        ]
        for pat in patterns:
            area = re.search(pat, add)
            if area is not None:
                return True
        return False
    
    @staticmethod
    def is_base_struct(line):
        """Return if is in line base structure for evaluation

        If line was empty, and now is there base structure, reload is needed
        """
        patterns = [
            r'\s*\S+\s*:',
            r'\s*!\S+\s',
            r'\s*&\S+\s',
            r'\s\*\S+\s',
            r'\s*-\s+',
            r'.*<<:\s+\*',
            r'.*\S+\s*,',
            r'.*\S+\s*\}',
            r'.*\S+\s*\]'
        ]
        line = LineAnalyzer.strip_comment(line)
        for pat in patterns:
            area = re.match(pat, line)
            if area is not None:
                return True
        return False
