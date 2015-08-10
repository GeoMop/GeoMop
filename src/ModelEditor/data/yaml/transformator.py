import json
import re
import data.data_node as dn
from data.yaml import DocumentParser
from data.error_handler import ErrorHandler

class Transformator:
    """Transform yaml file to new version"""
    
    def __init__(self,  transform_file):
        """init"""
        self._transformation = json.loads(transform_file)
        "parsed json transformation file"
        #check
        if  not 'actions' in  self._transformation:
            raise TransformationFileFormatError("Array of actions is required")
        i=1
        for action in self._transformation['actions']:
            self._check_parameter("action", action,  action['action'],  i)
            if not action['action'] in ["delete-key", "move-key",  "rename-type"]:
                raise TransformationFileFormatError(" Action '" + action.action + "' is nod specified")
            self._check_parameter("parameters", action,  action['action'],  i)
            if action['action'] == "delete-key":
                self._check_parameter("path", action['parameters'],  action['action'],  i)
            elif action['action'] == "move-key":
                self._check_parameter("destination_path", action['parameters'],  action['action'],  i)
                self._check_parameter("source_path", action['parameters'],  action['action'],  i)
            elif action['action'] == "rename-type":
                self._check_parameter("path", action['parameters'],  action['action'],  i)
                self._check_parameter("new_name", action['parameters'],  action['action'],  i)
                self._check_parameter("old_name", action['parameters'],  action['action'],  i)
            i += 1

    def _check_parameter(self,  name, dict, act_type,  line):
        if  not name in dict:
            raise TransformationFileFormatError("Parameter " + name +" for action type '" 
                + act_type + "' si required" + " (action: " + str(line) +")")
        if  dict[name] is None or dict[name] == "":
            raise TransformationFileFormatError("Parameter " + name +" for action type '" 
                + act_type + "' cannot be empty" + " (action: " + str(line) +")")
                    
    @property
    def old_version(self):
        """return version of yaml document befor transformation"""
        if  'old_format' in self._transformation:
            return self._transformation['old_format']
        return ""
    
    @property
    def new_version(self):
        """return version of yaml document after transformation"""
        if  'new_format' in self._transformation:
            return self._transformation['new_format']
        return ""
        
    @property
    def description(self):
        """return transformation description"""
        if  'description' in self._transformation:
            return self._transformation['description']
        return ""
        
    @property
    def name(self):
        """return transformation name"""
        if  'name' in self._transformation:
            return self._transformation['name']
        return ""

    def transform(self, yaml):
        """transform yaml file"""
        error_handler = ErrorHandler()
        doc_parser = DocumentParser(error_handler)
        changes = True
        for action in self._transformation['actions']:
            if changes:
                error_handler.clear()
                root = doc_parser.parse(yaml)
                lines = yaml.splitlines(False)
            if action['action'] == "delete-key":
                changes = self._delete_key(root, lines,  action)
            elif action['action'] == "move-key":
                changes = self._move_key(root, lines,  action)
            elif action['action'] == "rename-type":
                changes = self._rename_type(root, lines,  action)
            if changes:
                yaml = "\n".join(lines)
        return yaml

    def _delete_key(self, root, lines,  action):
        """Delete key transformation"""
        try:
            node = root.get_node_at_path(action['parameters']['path'])
        except:
            return False
        l1, c1, l2, c2 =self._get_node_pos(node)
        # try delete with comma after or prev
        nl2, nc2 = self._next_spread(lines, l2, c2)
        if nl2 == l2 and nc2 == c2:
           l1, c1 = self._prev_spred(lines, l1, c1)
        else:
            l2 = nl2
            c2 = nc2
        # try add comments
        l1, c1, l2, c2 = self._add_comments(lines, l1, c1, l2, c2)
        # one line
        if l1 == l2 :
            place = re.search('^(\s*)(\S.*\S)(\s*)$', lines[l1])
            if ((len(place.group(1))>=c1) and
                 ((len(lines[l1]) -  len(place.group(3))) <= c2)):
                del lines[l1]
            else:
                lines[l1] = lines[l1][:c1] + lines[l1][c2:]
        else:
            # more lines
            place = re.search('^(\s*)(\S.*\S)(\s*)$', lines[l2])
            if len(place.group(1))>c2:
                if (len(lines[l2]) - len(place.group(3))) <= c2:
                    del lines[l2]
                else:
                    lines[l2] = place.group(1) +lines[l2][c2:]
            for i in range(l2-1,l1,-1):
                del lines[i]                
            place = re.search('^(\s*)(\S.*)$', lines[l1])
            if len(place.group(1))>=c1:
                del lines[l1]
            else:
                lines[l1] = lines[l1][:c1] 
        return True
    
    @staticmethod
    def _next_spread(lines, line, column):
        """if next no-empty char is comma, return new possition"""
        old_line = line
        old_column = column
        while True:
            column += 1
            while len(lines[line]) <= column:
                column = 0
                line += 1
                if line<len(lines):
                    break
            if not lines[line][column].isspace():
                if lines[line][column] == ",":
                    return line, column
                break
        return old_line, old_column
        
    @staticmethod    
    def _prev_spred(lines, line, column):
        """if previous no-empty char is comma, return new possition"""
        old_line = line
        old_column = column
        while True:
            column -= 1
            while  0 > column:
                line -= 1
                if line < 0:
                    break 
                column = len(lines[line])-1
            if not lines[line][column].isspace():
                if lines[line][column] == ",":
                    return line, column
                break
        return old_line, old_column
        
    def _move_key(self, root, lines,  action):
        """Move key transformation"""
        try:
            parent1 = root.get_node_at_path(action['parameters']['destination_path'])
            raise TransformationFileFormatError("Destination path (" + 
                action['parameters']['destination_path'] + ") already exist")
        except:
            pass
        try:
            parent1 = re.search('^(.*)/([^/]*)$',action['parameters']['source_path'])
            node1 = root.get_node_at_path(action['parameters']['source_path'])
        except:
            return False 
        try:
            parent2 = re.search('^(.*)/([^/]*)$',action['parameters']['destination_path'])
            node2 = root.get_node_at_path(parent2.group(1))
        except:
            raise TransformationFileFormatError("Parent of destination path (" + 
                action['parameters']['destination_path'] + ") must exist")   
        sl1, sc1, sl2, sc2 =self._get_node_pos(node1)
        dl1, dc1, dl2, dc2 =self._get_node_pos(node2)
        if parent1.group(1) == parent2.group(1):
            #rename
            i = node1.key.span.start.line
            lines[i] = re.sub(parent1.group(2) + "\s*:", parent2.group(2) + ":", lines[i])
            return True
        if not isinstance(node2,  dn.CompositeNode):
            raise TransformationFileFormatError("Parent of destination path (" + 
                action['parameters']['destination_path'] + ") must be abstract record")
        intendation1 =  re.search('^(\s*)(\S.*)$', lines[dl1])
        intendation1 = len(intendation1.group(1)) + 2
        add = []
        # try add comments
        sl1, sc1, sl2, sc2 = self._add_comments(lines, sl1, sc1, sl2, sc2)       
        if sl1 == sl2:
            add.append(intendation1*" " + lines[sl1][sc1:sc2])
        else:            
            add.append(intendation1*" " + lines[sl1][sc1:])
            intendation2 = re.search('^(\s*)(\S.*)$', lines[sl1])
            intendation2 = len(intendation2.group(1))
            intendation = intendation1 - intendation2
            for i in range(sl1+1, sl2):
                intendation_test =  re.search('^(\s*)(\S.*)$', lines[i])
                if intendation==0 or len(intendation_test.group(1))<-intendation:
                    add.append(lines[i])
                elif intendation<0:
                    add.append(lines[i][-intendation:])
                else:                
                    add.append(intendation*" " + lines[i])
            intendation_test = re.search('^(\s*)(\S.*)$', lines[sl2])
            if len(intendation_test.group(1)) < sc2:
                if intendation==0 or len(intendation_test.group(1))<-intendation:
                    add.append(lines[i][:sc2])
                elif intendation<0:
                    add.append(lines[i][-intendation:sc2])
                else:                
                    add.append(intendation*" " + lines[i][:sc2])
        i = node1.key.span.start.line - sl1 - 1
        add[i] = re.sub(parent1.group(2) + "\s*:", parent2.group(2) + ":", add[i])
        if sl2 < dl1 or (sl2 == dl1 and sc2<dc1):            
            # source before dest, first copy 
            intendation2 =  re.search('^(\s*)(\S.*)$', lines[dl2])
            for i in range(len(add)-1, -1, -1):
                if len(intendation2.group(1)) < dc2:
                    #to end file
                    lines.insert(dl2+1, add[i])
                else:
                    lines.insert(dl2, add[i])
            action['parameters']['path'] = action['parameters']['source_path']
            self._delete_key(root, lines,  action)
        elif dl2 < sl1 or (dl2 == sl1 and dl2<sc1):
            # source after dest, first delete
            action['parameters']['path'] = action['parameters']['source_path']
            self._delete_key(root, lines,  action)
            intendation2 =  re.search('^(\s*)(\S.*)$', lines[dl2])
            for i in range(len(add)-1, -1, -1):
                if len(intendation2.group(1)) < dc2:
                    #to end file
                    lines.insert(dl2+1, add[i])
                else:
                    lines.insert(dl2, add[i])
        else:            
            raise TransformationFileFormatError("Destination block (" +
                action['parameters']['source_path'] +
                ") and source block (" + action['parameters']['destination_path'] +
                " is overlaped")
            
    def _rename_type(self, root, lines,  action):
        """Rename type transformation"""
        try:
            node = root.get_node_at_path(action['parameters']['path'])
        except:
            return False
        old = '!' + action['parameters']['old_name']  + ' '
        new = '!' + action['parameters']['new_name']  + ' '
        l1, c1, l2, c2 =self._get_node_pos(node)
        for i in range(l1, l2+1):
            lines[i] = re.sub(old, new, lines[i])
        return False # reload is not necessary
            
    @staticmethod
    def _get_node_pos(node):
        """return possition of node in file"""
        return node.start.line-1, node.start.column-1, \
            node.end.line-1, node.end.column-1
        
    @staticmethod
    def _add_comments(lines, l1 , c1, l2, c2):
        """Try find comments before node and add it to node"""
        nl1=l1;
        nc1=c1;
        nl2=l2;
        nc2=c2;
        # comments before
        inten = re.search('^(\s*)(\S+).*$', lines[l1])
        if inten is not None and len(inten.group(1)) >= c1:
            while nl1>0:
                comment = re.search('^(\s*)#\s*(\S+.*)$', lines[nl1-1])
                if comment is not None:
                    nl1 -= 1
                    nc1 = 0
                else:
                    break
        if nl1 != l1:
            inten = re.search('^(\s*)(\S+).*$', lines[nl1])
            nc1 = len(inten.group(1))
        # comments after
        inten = re.search('^(.*\S)\s*#\s*\S+.*$', lines[l2])
        if inten is not None and len(inten.group(1)) <= c2:
            nc2=len(lines[nl2])
            while nl2<len(lines)-1:
                comment = re.search('^(\s*)#\s*(\S+.*)$', lines[nl2+1])
                if comment is not None:
                    nl2 += 1
                    nc2=len(lines[nl2]) 
                else:
                    break
        return nl1, nc1, nl2, nc2                

class TransformationFileFormatError(Exception):
    """Represents an error in transformation file"""
    
    def __init__(self, msg):
        super(TransformationFileFormatError, self).__init__(msg)
        
