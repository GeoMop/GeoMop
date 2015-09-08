"""Helper for yaml text editor"""
from enum import Enum
import re
import copy

class SubYamlChangeAnalyzer:
    """
    Alalize partial yaml text for change character report
    
    Description: This quick party text analizing is use only for dicision
    if next more expensive text parsing is requard.
    """
    def __init__(self, cursor_line, cursor_index,  area):
        self._area = copy.deepcopy(area)
        for line in range(0, len(self._area)):
            if self._area[line][-1:] == "\n":
                self._area[line] = self._area[line] [0:-1]
        self._line = cursor_line
        self._index = cursor_index
        if len(self._area[self._line]) <= self._index:
            self._index = len(self._area[self._line]) - 1 

    @staticmethod
    def get_char_poss(line, tag):
        """Return possition of tag ended by space or new line"""
        index =  line.find(tag + " ")
        if index == -1:
            index =  line.find(tag)
            if index > -1 and len( line) != (index+1):
                return -1
        return index
        
    def get_pos_type(self):
        """return line type enum value"""
        is_key = False
        jsonList = 0
        inner = False
        i = 0
        while i < len(self._area):
            #key
            index = self.get_char_poss(self._area[i], ":")
            if  not is_key:                
                if index > -1:
                    nline, nindex = self._get_key_area(i)
                    if  self._line<nline or (self._line == nline and self._index <= nindex):
                        return PosType.in_key
                    i = nline
                is_key = True
                if self.get_char_poss(self._area[i][index+1:], ":")>-1: 
                    inner = True
            else: 
                if index>-1:
                    inner = True
            #inner
            if not inner and i > 0:
                start = re.match('^\s*-\s+\S', self._area[i])
                if start:
                    inner = True
            #multiline - not resolve 
            index = self._area[i].find( "|")
            if index==-1:
               index = self._area[i].find( ">")
            if index == len(self._area[i])-1:
                if inner:
                     return PosType.in_inner
                return PosType.in_value
            #comment
            index =  self._area[i].find( "#")
            if index > -1:
                if self._line == i and self._index > index:
                        return PosType.comment
            #json list +
            index = self._area[i].find( "[")
            while index > -1:
                jsonList += 1
                index = self._area[i].find( "[", index+1)
            index = self._area[i].find( "{")
            while index > -1:
                jsonList += 1
                index = self._area[i].find( "{", index+1)
            #json           
            if i == self._line:               
                if jsonList > 0:
                    if(self._area[i][self._index] == " " or self._area[i][self._index] == "," or
                        self._area[i][self._index] == "[" or self._area[i][self._index] == "]" or
                        self._area[i][self._index] == "{" or self._area[i][self._index] == "}"):
                            return PosType.in_value
                    return PosType.in_inner
            index = self._area[i].find( "]")
            #json-
            while index > -1:
                jsonList -= 1
                index = self._area[i].find( "]", index+1)
            index = self._area[i].find( "}")
            while index > -1:
                jsonList -= 1
                index = self._area[i].find( "}", index+1)
            #inner process
            if inner and i == self._line:
                start = re.search('^\s*-\s\S', self._area[i])                
                if not start:
                    start = re.search('^\s*\S', self._area[i])
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
        is_dist, dist = self.get_key_area(self._area[i])
        if not is_dist:
            return line, 0
        if dist != -1:
            return i, dist-1
        while dist == -1:
            i = i + 1
            if i >= len(self._area):
                return i, 0
            is_dist, dist = self.get_key_area(self._area[i])
            if is_dist:
                if dist != -1:
                    return i, dist-1
            else:
                return i , 0

    def get_key_pos_type(self):
        """return key type pos"""
        i = 0
        dist = 0
        type = KeyType.key
        
        next_line = False
        while i <= self._line:
            line = self.uncomment(self._area[i])
            key = re.match('[^:]+:\s*$', line)
            if key is not None:
                if self._line == i:
                    return type
                next_line = True                
                break
            key = re.match('([^:]+:\s)', line)
            if key is not None:
                if self._line == i and self._index<key.end(1):
                    return type
                line = line[key.end(1):]
                dist += key.end(1)
                break
            
        next_line = False
        while i <= self._line:
            if next_line:
                i += 1
                if i > self._line:
                    return type
                line = self.uncomment(self._area[i])
                if line.isspace() or len(line)==0:
                    continue
                dist = 0
                next_line = False                
            for char in ['!','&', '<<: *', '*' ]:
                index = line.find(char)
                if index > -1:
                    area = re.match('\s*(' + char + '\S+\s*)$',line)
                    if area is not None:
                        # area is all line
                        if self._line == i:
                            return self. _get_type_from_char(char)
                        next_line = True
                        break
                    else:
                        area = re.match('\s*(' + char + '\S+\s+)\S',line)
                        if area is not None:
                            if self._line == i and self._index<(area.end(1)+dist):
                                return self. _get_type_from_char(char)
                            line = line[area.end(1):]
                            dist += area.end(1)
                            type = self. _get_type_from_char(char)
                            break
        return type

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
            
    @classmethod
    def get_key_area(cls, line):
        """
        get key area for 1\one line
        
        return if is, end_of_arrea (-1 end of line)
        """
        key = re.match('[^:]+:\s*$', line)
        if key is not None:
            return True, -1
        key = re.match('([^:]+:\s)', line)
        if key is not None:
            dist = key.end(1)
            res, dist2 = cls.get_after_key_area(line[dist:])
            if not res:
                return True, dist
            if dist2 == -1:
                return True, -1
            return True, dist + dist2
        return False,  0

    @classmethod
    def get_after_key_area(cls, line):
        """
        Test if line begin with special areas (tag, ref, anchor)
        
        return if is, end_of_arrea (-1 end of line)
        """
        line = cls.uncomment(line)
        area = re.match('\s*$',line)
        if area is not None:
            # empty line
            return True, -1
        for char in ['!','&', '<<: *', '*' ]:
            index = line.find(char)
            if index > -1:
                area = re.match('\s*(' + char + '\S+\s*)$',line)
                if area is not None:
                    # area is all line
                    return True, -1
                area = re.match('\s*(' + char + '\S+\s+)\S',line)
                if area is not None:
                    dist = area.end(1)
                    res, dist2 = cls.get_after_key_area(line[dist:])
                    if not res:
                        return True, dist
                    if dist2 == -1:
                        return True, -1
                    return True, dist + dist2
        return False,  0
  
    @staticmethod
    def is_base_struct(line):
        """return if is in line created base structure for evaluation"""
        patterns = [
                '#\s*\S',
                '\S\s*:\s+\S',
                '<<:\s*\S',
                '{\s*\S',
                '\[\s*\S',
                '-\s+\S',
                '\S\s*,\s*\S'
            ]
        for pat in patterns:
            area = re.search(pat,line)
            if area is not None:
                return True
        return False        
        
  
    @staticmethod
    def uncomment(line):
        """return line witout comments"""
        comment = re.search('^(.*\S)\s*#.*$', line)
        if comment:           
            return comment.group(1)
        else:
            return line        
      
    @staticmethod  
    def indent_changed(new_row,  old_row):
        """compare intendation two rows"""
        if old_row.isspace() or len(old_row) == 0:
            return False
        old_value = re.search('^\s*\S', old_row)
        new_value = re.search('^\s*\S', new_row)
        if not old_value and not new_value:
            return False
        if not old_value or not new_value:
            return True
        return not len(old_value.group(0)) == len(new_value.group(0))
    
class PosType(Enum):
    comment = 1
    in_key = 2
    in_value = 3
    in_inner = 4
    
class KeyType(Enum):
    key = 1
    tag = 2
    ref = 3
    ref_a = 4
    anch = 5
    
class CursorType(Enum):
    key = 1
    tag = 2
    ref = 3
    anch = 4
    value = 5
    other = 6
    
    @staticmethod
    def get_cursor_type(pos_type, key_type):
        """return type below cursor from PosType and KeyType"""
        if pos_type is PosType.in_key:
            if key_type is KeyType.key:
                return CursorType.key
            if key_type is KeyType.tag:
                return CursorType.tag
            if key_type is KeyType.anch:
                return CursorType.anch
            return CursorType.ref
        if pos_type is PosType.in_value:
            return CursorType.value
        return CursorType.other
