"""Helper for yaml text editor"""
from enum import Enum
import re

class SubYamlChangeAnalyzer:
    """
    Alalize partial yaml text for change character report
    
    Description: This quick party text analizing is use only for dicision
    if next more expensive text parsing is requard.
    """
    def __init__(self, cursor_line, cursor_index,  area):
        self._area = area
        self._line = cursor_line
        self._index = cursor_index

    @staticmethod
    def get_tag_poss(line, tag):
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
        for i in range(0, len(self._area)):
            #key
            index = self.get_tag_poss(self._area[i], ":")
            if  not is_key:                
                if index > -1:
                    if  self._line<i or (self._line == i and self._index <= index):
                        return PosType.in_key
                is_key = True
                if self.get_tag_poss(self._area[i][index+1:], ":")>-1: 
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
        return PosType.in_value
    
    @staticmethod
    def uncomment(line):
        """return line witout comments"""
        comment = re.search('^(.*\S)\s*#.*$', line)
        if comment:           
            return comment.group(1)
        else:
            return line
        
    def key_changed(self, old_first_row):
        """find key and check id was changed"""
        old_key = re.search('^.*:', old_first_row)
        new_key = re.search('^.*:', self._area[0])
        if not old_key and not new_key:
            return False
        if not old_key or not new_key:
            return True
        return old_key.group(0).strip() != new_key.group(0).strip()
       
    def value_changed(self, old_first_row):
        """find value and check id was changed"""
        old_value = re.search(':\s*(.*)$', old_first_row)
        new_value = re.search(':\s*(.*)$', self._area[0])
        if not old_value and not new_value:
            return False
        if not old_value or not new_value:
            return True
        return (self.uncomment(old_value.group(1)).strip() != 
                      self.uncomment(new_value.group(1)).strip())
      
    @staticmethod  
    def indent_changed(new_row,  old_row):
        """compare intendation two rows"""
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
    
