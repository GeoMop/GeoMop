# -*- coding: utf-8 -*-
"""
GeomMop configuration file parsers

This file contains the parsing functions for configuration files of Flow123d.
Currently supports .con format (as specified by Flow123d manual v1.8.2).
"""
import yaml
import demjson
import re
#from copy import copy
import data.data_node as dn
from enum import Enum

def parse_con(con):
    """
    Parses a configuration file of Flow123d in .con format with given filename.

    Returns the yaml text structure.
    """
    data = _decode_con(con)    
    data = yaml.dump(data, default_flow_style=False, indent=2)
    return data
    
def rewrite_comments(con, yaml, data):
    """Read comments from text (con file) and place it to yaml structure"""
    pattern = re.compile(r"\s?=\s?")  # TODO can I replace = simply like this?
    con = pattern.sub(':', con)
    comments = Comments()
    comments.read_comments_from_con(con, data)
    comments.sorte_by_yaml(yaml, data)
    return comments.write_to_yaml(yaml)
    
def _decode_con(con):
    """Reads .con format and returns read data in form of dicts and lists."""
    pattern = re.compile(r"\s?=\s?")  # TODO can I replace = simply like this?
    con = pattern.sub(':', con)
    return demjson.decode(con)
    
def fix_tags(yaml, root):
    """Replase TYPE and refferences by tags"""
    lines = yaml.splitlines(False)
    add_anchor = {}
    anchor_idx = {}
    del_lines = _traverse_nodes(root, lines, add_anchor, anchor_idx)
    new_lines = []
    for i in add_anchor:
        try:
            anchor = root.get_node_at_path(i)
            col = anchor.span.start.column-1
            line = anchor.span.start.line-1
            if anchor.key.span is not None:
                col = anchor.key.span.end.column-1
                line = anchor.key.span.end.line-1
                if len(lines[line])>col+1:
                    text = lines[line][:col]
                    tag = re.search('^(\s+!\S+)',text)
                    col += tag.group(1)
            if len(lines[line])>col+1:
                lines[line] = lines[line][:col] + " &anchor" + str(anchor_idx[i]) + ' ' +  lines[line][col:]
            else:
                lines[line] += " &anchor" + str(anchor_idx[i])
        except:
            continue
    for i in range(0, len(lines)):
        if i not in del_lines:
            new_lines.append(lines[i])            
    return "\n".join(new_lines)
 
def _traverse_nodes(node, lines, add_anchor, anchor_idx, i=1):
    """
    Traverse node, recursively call function for children,
    resolve type to tag and resolve refferences.
    
    return: array of lines for deleting
    """ 
    del_lines = []
    if isinstance(node, dn.CompositeNode):
        for child in node.children:
            if isinstance(child, dn.ScalarNode) and child.key.value == "TYPE":
                del_lines.append(child.key.span.start.line-1)
                lines[node.key.span.start.line-1] += " !" + child.value
            elif isinstance(child, dn.ScalarNode) and child.key.value == "REF":
                del_lines.append(child.key.span.start.line-1)
                lines[node.key.span.start.line-1] += " *anchor" + str(i)
                if child.value not in add_anchor:
                    add_anchor[child.value] = []
                    anchor_idx[child.value] = i
                    i += 1
                add_anchor[child.value].append(child)
            else:
                if isinstance(child, dn.CompositeNode):
                    del_lines.extend(_traverse_nodes(child, lines, add_anchor, anchor_idx, i))
    return del_lines
  
class Comment: 
    """Class for one comment"""

    def __init__(self, path, text, after=False):
        self.path = path
        if len(self.path)>4 and self.path[-4:] == "TYPE":
            self.path = self.path[:-4]
        if len(self.path)>3 and self.path[-3:] == "REF":
            self.path = self.path[:-3]
        """comment for key"""
        self.after = after
        """comment after key (else above key)"""
        self.rows = text.splitlines(False)
        """Array of comments"""
        self.pos = None
        """possition in associated file"""             
    
    def set_yaml_position(self, data):
        """set possition in yaml file"""
        node = data.get_node_at_path(self.path)
        self.pos = node.start

class Comments: 
    """Class for comments processed"""
    def __init__(self):
        self.comments = []
        """array of comments"""
    
    class BlokType(Enum):
        """Type of block"""
        array = 0
        dict = 1
     
    def read_comments_from_con(self, text, data):
        """reread comments from con file"""
        self.comments=[]
        path=""
        lines = text.splitlines(False)
        col = 0
        line = 0
        while True:
            comm, col, line = self._read_comment(col, line,  lines)
            if comm is not None:
                self.comments.append(Comment('/', comm, False))
            else:
                break;
        type, col, line = self._read_start_of_block( col, line,  lines)
        if type is None:
            return text
        self._traverse_child(col, line, type, lines, path, data)
        
    def _traverse_child(self, col, line, type, lines, path, data):
        """process all data in level and call recursivly itsself for next children"""
        res, col, line = self._read_end_of_block(col, line,  lines, type)
        if res:
            return col, line
        i=0
        while line<(len(lines)-1) or col<(len(lines[len(lines)-1])):                
            comm, col, line = self._read_comment(col, line,  lines)
            if type == self.BlokType.dict:
                key ,col, line = self._read_key(col, line, lines)
                if key is None:
                    res, col, line = self._read_end_of_block( col, line,  lines, type, False)
                    return col, line
                new_path = self._get_real_path(path,  key,  data)
                if new_path is None:
                    res, col, line = self._read_end_of_block( col, line,  lines, type, False)
                    return col, line
                if comm is not None:
                    self.comments.append(Comment(new_path, comm, False))
                comm, col, line = self._read_comment(col, line,  lines)
            else:
                new_path = self._get_real_path(path,  str(i),  data)
                i += 1
                if new_path is None:
                    res, col, line = self._read_end_of_block( col, line,  lines, type, False)                        
                    return col, line
            value, col, line = self._read_value(col, line, lines)                
            child_type, col, line = self._read_start_of_block(col, line,  lines)
            if comm is not None:
                self.comments.append(Comment(new_path, comm, False))                
            if child_type is not None:                    
                col, line = self._traverse_child(col, line, child_type, lines, new_path, data)
            else:
                value, col, line = self._read_value(col, line, lines)
            comm, col, line = self._read_comment(col, line,  lines)
            if comm is not None:
                self.comments.append(Comment(new_path, comm, True))
            res, col, line = self._read_end_of_block(col, line,  lines, type)
            if res:
                return col, line            
            res, col, line = self._read_sep(col, line,  lines) 
            if res:
                comm, col, line = self._read_comment(col, line,  lines, True)
                if comm is not None:
                    self.comments.append(Comment(new_path, comm, True))
            else:
                res, col, line = self._read_end_of_block( col, line,  lines, type, False)                        
                return col, line
    
    def sorte_by_yaml(self, yaml, data):
        """sorte comments by possition in yaml file"""
        for coment in self.comments:
            coment.set_yaml_position(data)
        self.comments = sorted(self.comments, key=lambda comment: comment.pos, reverse=True)
        ok = False
        while not ok:
            ok =True
            for i in range(1, len(self.comments)):
                if self.comments[i].pos.line == self.comments[i-1].pos.line:
                    if self.comments[i-1].after:
                        self.comments[i].rows.extend(self.comments[i-1].rows)
                        del self.comments[i-1]
                    else:
                        self.comments[i-1].rows.extend(self.comments[i].rows)
                        del self.comments[i]
                    ok = False
                    break
 
    def write_to_yaml(self, yaml):
        """return yaml text with comments"""
        lines = yaml.splitlines(False)
        for comment in self.comments:
            intend =  re.search('^(\s*)(\S.*)$', lines[comment.pos.line-1])
            if comment.after:
                if (len(lines[comment.pos.line])-1) <= comment.pos.column:
                    lines[comment.pos.line] += " # " + comment.rows[0]
                else:
                    lines.insert(comment.pos.line,  intend.group(1) + "# " + comment.rows[0])
            else:
                lines.insert(comment.pos.line-1,  intend.group(1) + "# " + comment.rows[0])
            for i in range(1, len(comment.rows)):
                if comment.after:
                    lines.insert(comment.pos.line+i,  intend.group(1) + "# " + comment.rows[i])
                else:
                    lines.insert(comment.pos.line+i-1,  intend.group(1) + "# " + comment.rows[i])
        return "\n".join(lines)
        
    def _read_key(self, col, line, lines):
        """
        find key in tex
        
        return key (succes) or None and new line and column
        """
        if line >= len(lines):                
            return None, col, line
        txt = lines[line][col:]
        i = 0
        prev_key = None
        icol, iline = self._find_all_interupt(col, line, lines)
        while True:
            key = re.search('^(\s*)(\S+)(\s*:)', txt)
            inter = None
            if line + i == iline:
                if i == 0:
                    inter = icol - col
                else:
                    inter = icol
            if key:
                if inter is not None:
                    end_key = len(key.group(1)) + len(key.group(2))
                    if end_key > inter:
                        return None, col, line
                    else:
                        if i == 0:
                            end_key += col
                        end_key += 1
                        if len(lines[line+i]) <= end_key:
                            icol = 0
                            i += 1
                        return self._trim(key.group(2)), end_key, line+i
            else:
                if inter is not None:
                    if prev_key is not None:
                        key = re.search('^(\s*):', txt)
                        if key is not None:
                            return self._trim(prev_key), key.span()[1], line+i
                    return None, col,  line
            key = re.search('^(\s*)$', txt)
            if key is None:
                if prev_key is not None:
                    return None, col, line
                key = re.search('^(\s*)(\S*)(\s*)$', txt)
                if key is None:
                    return None,  col, line
                else:
                    prev_key = key.group(2)
            i += 1
            if line+i >= len(lines):               
                return None,  col, line
            txt = lines[line+i]

    def _find_all_interupt(self, col,  line, lines):
        """
        find first interapt char
        
        return its possition
        """
        if line >= len(lines):                
            return col, line
        index = None
        ap=None
        text =  lines[line][col:]
        i = 0        
        for ch in ['[', ']', '{', '}', ',', '//', '/*','*/', ':']:
            sep = text.find(ch)
            if sep > -1 and (index is None or index>sep):
                index = sep
        for ch in ['"',"'"]:
            sep = text.find(ch)
            if sep > -1 and (ap is None or ap>sep):
                ap = sep
        if index is not None and (ap is None or ap>index):
            if i == 0:
                return index + col,  line + i
            else:
                return index,  line + i
        if ap is not None:
            chap = text[ap]
            begin = ap+1
            bi = i
            if i == 0:
                begin += col
            if len(lines[i+line]) <= begin:
                i += 1
                begin = 0
                if line+i >= len(lines):                
                    return 0, line+i
            text =  lines[line+i][begin:]
            while True:
                sep = text.find(chap)
                if sep > -1:
                    new_begin = sep + 1
                    if bi == i:
                        new_begin += begin
                    if len(lines[i+line]) <= new_begin:
                        i += 1
                        new_begin = 0
                        if line+i >= len(lines):                
                            return 0, line+i
                    return self._find_all_interupt(new_begin,  line+i, lines)
                i += 1                
                if line+i >= len(lines):                
                    return 0, line+i
                text =  lines[line+i]
        i += 1                
        if line+i >= len(lines):                
            return 0, line+i
        return self._find_all_interupt(0,  line+i, lines)
             
    def _trim(self, text):
        """trim white spaces and apostrofe"""
        if text is None:
            return None
        text = text.strip()
        if len(text)>1:
            if text[0] == '"' and text[-1] == '"':
                text = text[1:-1]
            if text[0] == "'" and text[-1] == "'":
                text = text[1:-1]
        return text
        
    def _read_value(self, col, line, lines):
        """
        find key in text
        
        return value (succes) or line and new line and column
        """
        if line >= len(lines):                
            return None, col, line
        txt = lines[line][col:]
        i = 0
        value = None
        icol, iline = self._find_all_interupt(col, line, lines)
        while True:
            inter = None
            if line+i == iline:
                if i == 0:
                    inter = icol - col
                else:
                    inter = icol
            if inter is None:
                if value is None:
                    value = txt.strip()
                else:
                    value += "\n" + txt.strip()
            else:
                if value is None:
                    txt = txt[0:inter]                    
                else:
                    value += "\n" + txt[0:inter].strip()
                end_col = inter
                if i==0:
                    end_col += col
                if len(lines[line+i]) <= end_col:
                    end_col=0
                    i += 1
                return self._trim(value), end_col, line+i
            i += 1
            if line+i >= len(lines):                
                return self._trim(value), 0, line+i
            txt = lines[line+i]
        

    def _read_comment(self, col, line,  lines, only_after=False):
        """
        find key in text

        return comment (succes) or None and new line and column
        """
        if only_after and col == 0:
            return None, col, line
        if line >= len(lines):                
            return None, col, line
        text = lines[line][col:]
        i = 0
        while True:
            index = None
            for ch in ['//', '/*']:
                sep = text.find(ch)
                if sep > -1 and (index is None or index>sep):
                    index = sep
            if index is not  None:
                intend = re.search('^(\s*)(\S*)', text)
                if len(intend.group(1))<index:
                    return None, col, line
                if text[index+1] == '/':
                    if len(text)<=index+2:
                        return None, 0,  line+i+1
                    ret = text[index+2:].strip()
                    if len(ret) == 0:
                        return None, 0,  line+i+1                    
                    return ret, 0,  line+i+1
                if only_after:
                    return None, col, line
                # /*
                if len(text)<=index+2:
                    text = ""
                else:
                    text = text[index+2:]
                ret = None
                ni = i
                while True:
                    sep = text.find("*/")
                    if sep > -1:
                        if ret is None:
                            ret = text[:sep].rstrip()
                        else:
                            if len(text[:sep].rstrip()) > 0: 
                                # last emty line ignore                               
                                ret += "\n" + text[:sep].rstrip()
                        end = sep+2
                        if i==0:
                            end += col
                        if i == ni:
                            end += index+2
                        if len(lines[i]) <= end:
                            if len(ret) == 0:
                                return None, 0, line+i+1
                            else:
                                return ret, 0, line+i+1
                        else:
                            if len(ret) == 0:
                                return None, end, line+i
                            else:
                                return ret, end, line+i
                    else:
                        if text.isspace() or len(text) == 0:
                            if ret is None:
                                if i>ni:
                                    # first emty line ignore
                                    ret = "\n"
                            else:
                                ret += "\n"
                        else:
                            if ret is None:
                                ret = text.rstrip()
                            else:
                                ret += "\n" + text.rstrip()
                    i += 1                
                    if line+i >= len(lines):                
                        return None, 0, line+i
                    text = lines[line+i]
            if len(text)>0 and not text.isspace():
                return None, col, line
            if only_after:
                return None, col, line
            i += 1                
            if line+i >= len(lines):                
                return None, col, line
            text =  lines[line+i]
        
    def _read_end_of_block(self, col, line,  lines, type, restricted=True):
        """
        try read end of block, and return its possition 

        return bool (succes) and new line and column
        """
        if line >= len(lines):                
            return False, col, line
        if type == self.BlokType.dict:
            char = '}'
        else:
            char = ']'
        icol, iline = self._find_all_interupt(col, line, lines)
        if len(lines)<=iline:
            if restricted:
                return False, col, line
            else:
                return False, icol, iline
        if not restricted:
            in_array=0
            in_dict=0
            icol, iline = self._find_all_interupt(icol, iline, lines)
            while lines[iline][icol] != char or in_array > 0 or in_dict >0:                
                if len(lines)<=iline:
                    return False, icol, iline
                if lines[iline][icol] == '{':
                    in_dict += 1
                if lines[iline][icol] == '}':
                    in_dict -= 1
                if lines[iline][icol] == '[':
                    in_array += 1
                if lines[iline][icol] == ']':
                    in_array -= 1
                icol += 1
                if len(lines[iline])<= icol:
                    iline += 1
                    icol = 0
                    if len(lines)<=iline:                    
                        return True, icol, iline
                icol, iline = self._find_all_interupt(icol, iline, lines)
            return True, icol, iline
        if lines[iline][icol] != char:
            return False, col, line
        text = lines[line][col:]
        i=0
        while len(text)==0 or text.isspace():
            i += 1
            if line+i >= len(lines):                
                return False, col, line
            text = lines[line+i]
        if iline == (line+i):
            if i==0:
                text_before = text[:icol-col]
            else:
                text_before = text[:icol]        
            if len(text_before)==0 or text_before.isspace():
                icol += 1
                if len(lines[iline]) <= icol:
                    icol = 0
                    iline += 1
                return True, icol, iline
        return False, col,  line
        
    def _read_sep(self, col, line,  lines):
        """
        try read sepparator, and return its possition 

        return bool (succes) and new line and column
        """
        if line >= len(lines):                
            return False, col, line
        icol, iline = self._find_all_interupt(col, line, lines)
        if len(lines)<=iline:
            return False, icol, iline
        if lines[iline][icol] != ',':
            return False, col, line
        text = lines[line][col:]
        i=0
        while len(text)==0 or text.isspace():
            i += 1
            if line+i >= len(lines):                
                return False, col, line
            text = lines[line+i]
        if iline == (line+i):
            if i==0:
                text_before = text[:icol-col]
            else:
                text_before = text[:icol]        
            if len(text_before)==0 or text_before.isspace():
                icol += 1
                if len(lines[iline]) <= icol:
                    icol = 0
                    iline += 1
                return True, icol, iline
        return False, col,  line
        
    def _read_start_of_block(self, col, line,  lines):
        """
        try read start of block, and return its possition 

        return type block (succes) and new line and column
        """
        if line >= len(lines):                
            return None, col, line
        icol, iline = self._find_all_interupt(col, line, lines)
        if len(lines)<=iline:
            return False, icol, iline
        if lines[iline][icol] == '[':
            type = self.BlokType.array
        elif lines[iline][icol] == '{':
            type = self.BlokType.dict
        else:
            return None, col, line
        text = lines[line][col:]
        i=0
        while len(text)==0 or text.isspace():
            i += 1
            if line+i >= len(lines):                
                return False, col, line
            text = lines[line+i]
        if iline == (line+i):
            if i==0:
                text_before = text[:icol-col]
            else:
                text_before = text[:icol]        
            if len(text_before)==0 or text_before.isspace():
                icol += 1
                if len(lines[iline]) <= icol:
                    icol = 0
                    iline += 1
                return type, icol, iline
        return None, col,  line
        
    def _get_real_path(self, path, key, data):
        """check path existence in data"""
        new_path = path + "/" + key
        if key == "TYPE" or key == "REF":
            try:
                node = data.get_node_at_path(path)
            except:
                return None
            return new_path
        try:
            node = data.get_node_at_path(new_path)
        except:
            try:                
                node = data.get_node_at_path(path)
                if isinstance(node,  dn.CompositeNode) and len(node.children) == 1:
                    new_path = path + "/0/" + key
                    node = data.get_node_at_path(new_path)
                else:
                    return None
            except:
                return None
            return False
        return new_path               

    
    
