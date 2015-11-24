"""Structure changer.


.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""
import re

class StructureChanger:
    """
    Function for formating and adding yaml text
    Note:
        This class use l1, c1, l2, c2 instad  Position and Span classes.
        When I created it, I wasn't using it. I was thinking about rafactoring,
        but in classes where is StructureChanger used, is using l1, c1, l2, c2
        more comfort. There is a lot various comparation, assignation and 
        other operations of itself variables, that code is shorter and more clearly.
        
        Use  node_pos and value_pos for conversion from span to 
        l1, c1, l2, c2.
    """
    __indent__ = 2
    """File default indentation"""
    __line_length__ = 60
    """File default indentation"""    
    
    def __init__(self):
        """init"""
        pass

    @staticmethod
    def node_pos(node):
        """return position of node in file"""
        return node.start.line-1, node.start.column-1, node.end.line-1, node.end.column-1
    
    @staticmethod
    def value_pos(node):
        """return value position in file of set node """
        return node.span.start.line-1, node.span.start.column-1, \
            node.span.end.line-1, node.span.end.column-1
            
    @staticmethod
    def key_pos(node):
        """return key position in file of set node """
        if node.key is not None and node.key.span is not None:
            return node.key.span.start.line-1, node.key.span.start.column-1, \
                node.key.span.end.line-1, node.key.span.end.column-1
        return node.start.line-1, node.start.column-1, \
            node.start.line-1, node.start.column,
            
    @staticmethod
    def paste_structure(lines, line, add,  after_line, strip_empty=False):
        """
        Paste add structure accoding after_line parameter 
        before or after set possion.
        """        
        for i in range(len(add)-1, -1, -1):
            if not strip_empty or (len(add[i]) > 0 and not add[i].isspace()):
                if after_line:
                    # to end file
                    lines.insert(line+1, add[i])
                else:
                    lines.insert(line, add[i])
                    
    @staticmethod
    def copy_absent_path(lines, source, dest, add):
        """
        Add absent path (difference between source_path and dest_path ) 
        to add array and icrease its indentation.
        """
        source = path.split('/')
                    
    @staticmethod
    def change_tag(lines, node, old,  new):
        """change node tag"""        
        l1, c1, l2, c2 = StructureChanger.node_pos(node)
        return StructureChanger._replace(lines, new,  old,  l1, c1, l2, c2 )        
        
    @staticmethod
    def add_tag(lines, node, new):
        """add node tag"""
        l1, c1, l2, c2 = StructureChanger.key_pos(node)
        return StructureChanger._replace(lines, ': ' + new,  ":",  l1, c1, l2, c2 )
        
    
    @staticmethod    
    def replace(self, lines, new,  old,  l1, c1, l2, c2 ):
        """replace first occurence of defined value, and return if is len updated"""        
        for i in range(l1, l2+1):
            if i == l1:
                prefix =  lines[i][:c1]
                line =  lines[i][c1:]
            else:
                prefix =  ""                
                line =  lines[i]
            old_str = re.search(re.escape(old), line)
            if old_str is not None:
                if i == l2:
                    if (old_str.end() + len(prefix)):
                        return False
                if old_str.end() == len(line):
                    lines[i] = prefix + line[:old_str.start()] + new
                else:
                    lines[i] = prefix + line[:old_str.start()] + new + line[old_str.end():]
                if i == l2:
                    return len(new) != len(old)
                return False          
        return False
        
        
    @staticmethod
    def delete_structure(lines, l1, c1, l2, c2):
        """Delete structure from yaml file (lines array)"""
        if l1 == l2:
            place = re.search(r'^(\s*)(\S.*\S)(\s*)$', lines[l1])
            if ((len(place.group(1)) >= c1) and
                    ((len(lines[l1]) - len(place.group(3))) <= c2)):
                del lines[l1]
            else:
                lines[l1] = lines[l1][:c1] + lines[l1][c2:]
        else:
            # more lines
            place = re.search(r'^(\s*)(\S.*\S)(\s*)$', lines[l2])
            if place is not None:
                if len(place.group(1)) > c2:
                    if (len(lines[l2]) - len(place.group(3))) <= c2:
                        del lines[l2]
                    else:
                        lines[l2] = place.group(1) + lines[l2][c2:]
            else:
                del lines[l2]
            for i in range(l2-1, l1, -1):
                del lines[i]
            place = re.search(r'^(\s*)(\S.*)$', lines[l1])
            if place is not None:
                if len(place.group(1)) >= c1:
                    del lines[l1]
                else:
                    lines[l1] = lines[l1][:c1]
            else:
                del lines[l1]

    @staticmethod
    def copy_structure(lines, l1, c1, l2, c2, indent):
        """
        Copy structure from lines to separate array. Structure is
        move by indentation. 
        """
        add = []
        # try add comments
        if l1 == l2:
            add.append(indent*" " + lines[l1][c1:c2])
        else:
            from_line = l1
            if c1 > 0:
                add.append(indent*" " + lines[l1][c1:])
                from_line += 1
            indentation2 = re.search(r'^(\s*)(\S.*)$', lines[l1])
            indentation2 = len(indentation2.group(1))
            indentation = indent - indentation2
            for i in range(from_line, l2):
                indentation_test = re.search(r'^(\s*)(\S.*)$', lines[i])
                if indentation == 0 or len(indentation_test.group(1)) < -indentation:
                    add.append(lines[i])
                elif indentation < 0:
                    add.append(lines[i][-indentation:])
                else:
                    add.append(indentation*" " + lines[i])
            indentation_test = re.search(r'^(\s*)(\S.*)$', lines[l2])
            if len(indentation_test.group(1)) <= c2:
                if indentation == 0 or len(indentation_test.group(1)) < -indentation:
                    add.append(lines[l2][:c2])
                elif indentation < 0:
                    add.append(lines[l2][-indentation:c2])
                else:
                    add.append(indentation*" " + lines[l2][:c2])
        return add
        
    @staticmethod
    def skip_tar(self, lines, l1, c1, l2, c2):
        """
        Return start possition of value from set possition of node. 
        ( Start node structure witout tag, anchor or ref )               
        """
        for char in ["!", r'\*', r'<<:\s*\*', "&"]:
            nl1 = l1
            nc1 = c1
            if lines[nl1][nc1:].isspace() or len(lines[nl1]) <= nc1:
                nl1 += 1
                nc1 = 0
                if nl1 > l2:
                    return l1, c1
                while lines[nl1].isspace() or len(lines[nl1]) == 0:
                    nl1 += 1
                    if nl1 > l2:
                        return l1, c1
            tag = re.search(r'^(\s*' + char + r'\S*)', lines[nl1][nc1:])
            if tag is not None:
                nc1 += len(tag.group(1))
                if len(lines[nl1]) >= nc1:
                    nl1 += 1
                    nc1 = 0
                    if nl1 > l2:
                        return l1, c1
                c1 = nc1
                l1 = nl1
        return l1, c1
        
    @staticmethod
    def _add_comments(lines, l1, c1, l2, c2):
        """Try find comments before and after node and add it to node"""
        nl1 = l1
        nc1 = c1
        nl2 = l2
        nc2 = c2
        # comments before
        inten = re.search(r'^(\s*)(\S+).*$', lines[l1])
        if inten is not None and len(inten.group(1)) >= c1:
            while nl1 > 0:
                comment = re.search(r'^(\s*)#\s*(.*)$', lines[nl1-1])
                if comment is not None:
                    nl1 -= 1
                    nc1 = 0
                else:
                    break
        if nl1 != l1:
            inten = re.search(r'^(\s*)(\S+).*$', lines[nl1])
            nc1 = len(inten.group(1))
        # comments after
        inten = re.search(r'^(.*\S)\s*#\s*\S+.*$', lines[l2])
        if inten is not None and len(inten.group(1)) <= c2:
            nc2 = len(lines[nl2])
        # delete all line comment after
        if c2 == 0:
            comment = re.search(r'^(\s*)#\s*(.*)$', lines[nl2-1])
            if comment is not None:
                nl2 -= 1
                nc2 = len(lines[nl2])
        while nl2 > nl1:
            comment = re.search(r'^(\s*)#\s*(.*)$', lines[nl2])
            if comment is not None:
                nl2 -= 1
                nc2 = len(lines[nl2])
            else:
                break
        return nl1, nc1, nl2, nc2
        
    @staticmethod
    def _leave_comments(lines, l1, c1, l2, c2):
        """Try find comments in start and end of node and exclude it from node"""
        nl1 = l1
        nc1 = c1
        nl2 = l2
        nc2 = c2
        # comments on start
        comment = re.search(r'^(\s*)#\s*(.*)$', lines[l1][c1:])
        if comment is not None:
            nl1 += 1
            nc1 = 0
            while nl1 < nl2:
                comment = re.search(r'^(\s*)#\s*(.*)$', lines[nl1])
                if comment is not None:
                    nl1 += 1
                else:
                    break
        while nl2 > nl1:
            comment = re.search(r'^(\s*)#\s*(.*)$', lines[nl2][:nc2])
            if comment is None:
                if nc2 == 0 or lines[nl2][:nc2].isspace():
                    comment = re.search(r'^(\s*)#\s*(.*)$', lines[nl2-1])
                    if comment is None:
                        break
                    else:
                        nl2 -= 1
                        nc2 = 0
                else:
                    nc2 = 0
            ident = re.search(r'^(\s*)\S', lines[nl2])
            if ident is not None:
                nc2 = len(ident.group(1))
        return nl1, nc1, nl2, nc2    
