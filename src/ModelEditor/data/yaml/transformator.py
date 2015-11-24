"""
File for transformation of yaml files to another version

Actions:
    - move-key - Move value of set key from source_path to destination_path.
      Not existing directory of destination_path cause exception. If both path
      is same, only key is different, key is renamed. Destination_path placed in
      source_path cause exception. If source_path not exist action si skipped.
      Refference or anchors is moved and if its relative possition is changed,
      result must be fixed by user.
    - delete-key - Delete key on set path. If key contains anchor or refference,
      transporter try resolve reference. If path not exist action si skipped.
    - rename-type - Change tag on set path from old_name to new_name.
    - change-value - Change value on set path from old_value to new_value.
      If node in specified path is not scallar type nide, exception is raise.
    - merge-arrays - Add array in addition_path after array in source path. If
      destination_path is defined, move array to this path.

Description:
    Transformator check se json transformation file. If this file is in bad format,
    cause exception. After checking is processet action in set order. Repetitional
    processing this program can cause exception or corrupt data.

Example::

    {
        "name": "Example file",
        "description": "Template for creating transformation file",
        "old_format": "",
        "new_format": "",
        "actions": [
            {
                "action": "move-key",
                "parameters":{
                    "source_path":"/problem/primary_equation/input_fields",
                    "destination_path":"/problem/mesh/balance"
                }
            },
            {
                "action": "delete-key",
                "parameters": {
                    "path": "/problem/mesh/mesh_file"
                }
            },
            {
                "action": "rename-type",
                "parameters": {
                    "path": "/problem/primary_equation",
                    "old_name": "Steady_MH",
                    "new_name": "SteadyMH"
                }
            }
        ]
    }

"""

# pylint: disable=invalid-name

import json
import re

from .loader import Loader
from ..data_node import DataNode
from helpers import NotificationHandler
from helpers.subyaml import StructureChanger

class Transformator:
    """Transform yaml file to new version"""

    def __init__(self, transform_file, data=None):
        """init"""
        if transform_file is not None:
            self._transformation = json.loads(transform_file)
        else:
            self._transformation = data
        "parsed json transformation file"
        # check
        if not 'actions' in  self._transformation:
            raise TransformationFileFormatError("Array of actions is required")
        i = 1
        for action in self._transformation['actions']:
            self._check_parameter("action", action, action['action'], i)
            if not action['action'] in \
                    ["delete-key", "move-key", "rename-type", "move-key-forward", "change-value", "merge-arrays"]:
                raise TransformationFileFormatError(
                    " Action '" + action['action'] + "' is not specified")
            self._check_parameter("parameters", action, action['action'], i)
            if action['action'] == "delete-key":
                self._check_parameter("path", action['parameters'], action['action'], i)
            elif action['action'] == "move-key-forward":
                self._check_parameter("path", action['parameters'], action['action'], i)
            elif action['action'] == "move-key":
                self._check_parameter("destination_path", action['parameters'], action['action'], i)
                self._check_parameter("source_path", action['parameters'], action['action'], i)
            elif action['action'] == "rename-type":
                self._check_parameter("path", action['parameters'], action['action'], i)
                self._check_parameter("new_name", action['parameters'], action['action'], i)
                self._check_parameter("old_name", action['parameters'], action['action'], i)
            elif action['action'] == "change-value":
                self._check_parameter("path", action['parameters'], action['action'], i)
                self._check_parameter("new_value", action['parameters'], action['action'], i)
                self._check_parameter("old_value", action['parameters'], action['action'], i)
            elif action['action'] == "merge-arrays":
                self._check_parameter("source_path", action['parameters'], action['action'], i)
                self._check_parameter("addition_path", action['parameters'], action['action'], i)
            i += 1

    def _check_parameter(self, name, dict_, act_type, line):
        if name not in dict_:
            raise TransformationFileFormatError(
                "Parameter " + name + " for action type '" + act_type + "' si required" +
                " (action: " + str(line) + ")")
        if dict_[name] is None or dict_[name] == "":
            raise TransformationFileFormatError(
                "Parameter " + name + " for action type '" + act_type + "' cannot be empty" +
                " (action: " + str(line) + ")")

    @property
    def old_version(self):
        """return version of yaml document befor transformation"""
        if 'old_format' in self._transformation:
            return self._transformation['old_format']
        return ""

    @property
    def new_version(self):
        """return version of yaml document after transformation"""
        if 'new_format' in self._transformation:
            return self._transformation['new_format']
        return ""

    @property
    def description(self):
        """return transformation description"""
        if 'description' in self._transformation:
            return self._transformation['description']
        return ""

    @property
    def name(self):
        """return transformation name"""
        if 'name' in self._transformation:
            return self._transformation['name']
        return ""

    def transform(self, yaml):
        """transform yaml file"""
        notification_handler = NotificationHandler()
        loader = Loader(notification_handler)
        changes = True
        for action in self._transformation['actions']:
            if changes:
                notification_handler.clear()
                root = loader.load(yaml)
                lines = yaml.splitlines(False)
            if action['action'] == "delete-key":
                changes = self._delete_key(root, lines, action)
            elif action['action'] == "move-key":
                changes = self._move_key(root, lines, action)
            elif action['action'] == "rename-type":
                changes = self._rename_type(root, lines, action)
            elif action['action'] == "move-key-forward":
                changes = self._move_key_forward(root, lines, action)
            elif action['action'] == "change-value":
                changes = self._change_value(root, lines, action)
            elif action['action'] == "change-value":
                changes = self._add_array(root, lines, action)
                if changes and 'destination_path' in action['parameters']:                    
                    yaml = "\n".join(lines)
                    notification_handler.clear()
                    root = loader.load(yaml)
                    lines = yaml.splitlines(False)
                    changes = self._move_key(root, lines, action)
            if changes:
                yaml = "\n".join(lines)
        return yaml

    def _find_all_ref(self, node, refs):
        """find all references"""
        for child in node.children:
            if child.anchor is not None and child.ref is not None:
                if child.anchor.value not in refs:
                    refs[child.anchor.value] = {}
                    refs[child.anchor.value]['anchor'] = child.ref
                    refs[child.anchor.value]['ref'] = [child]
                else:
                    refs[child.anchor.value]['ref'].append(child)
            if not child.implementation == DataNode.Implementation.scalar:
                self._find_all_ref(child, refs)

    def _move_key_forward(self, root, lines, action):
        """Move key forward"""
        try:
            parent = re.search(r'^(.*)/([^/]*)$', action['parameters']['path'])
            node = root.get_node_at_path(action['parameters']['path'])
            if parent is None:
                raise TransformationFileFormatError(
                    "Cannot find parent path for path (" + action['parameters']['path'] + ")")
            is_root = False
            if len(parent.group(1)) == 0:
                parent_node = root
                is_root = True
            else:
                parent_node = root.get_node_at_path(parent.group(1))
        except:
            return False
        l1, c1, l2, c2 = self._get_node_pos(node)
        pl1, pc1, pl2, pc2 = parent_node.span.start.line-1, parent_node.span.start.column-1, \
            parent_node.span.end.line-1, parent_node.span.end.column-1
        if parent_node.implementation != DataNode.Implementation.mapping:
            raise TransformationFileFormatError(
                "Parent of path (" + action['parameters']['path'] + ") must be abstract record")
        if is_root:
            intendation1 = 0
            pl1 = 0
            pc1 = 0
        else:
            intendation1 = re.search(r'^(\s*)(\S.*)$', lines[pl1])
            intendation1 = len(intendation1.group(1)) + 2
        l1, c1, l2, c2 = self._add_comments(lines, l1, c1, l2, c2)
        add = StructureChanger.copy_structure(lines, l1, c1, l2, c2, intendation1)
        pl1, pc1 = self._skip_tar(lines, pl1, pc1, pl2, pc2)
        self._delete_key(root, lines, action)
        for i in range(len(add)-1, -1, -1):
            if pc1 == 0:
                lines.insert(pl1, add[i])
            else:
                lines.insert(pl1+1, add[i])
        return True

    def _delete_key(self, root, lines, action):
        """Delete key transformation"""
        try:
            node = root.get_node_at_path(action['parameters']['path'])
        except:
            return False
        l1, c1, l2, c2 = self._get_node_pos(node)
        anchors = []
        for i in range(l1, l2+1):
            if l1 == l2:
                text = lines[l1][c1:c2]
            elif i == l1:
                text = lines[l1][c1:]
            elif i == l2:
                text = lines[l2][:c2]
            else:
                text = lines[i]
            anchor = re.search(r'\s+&\s*(\S+)\s+', text)
            if anchor is None:
                anchor = re.search(r'\s+&\s*(\S+)$', text)
            if anchor is not None:
                anchors.append(anchor.group(1))
        if len(anchors) > 0:
            self._rewrite_first_ref(root, lines, anchors)
        # try delete with comma after or prev
        nl2, nc2 = self._next_spread(lines, l2, c2)
        if nl2 == l2 and nc2 == c2:
            l1, c1 = self._prev_spred(lines, l1, c1)
        else:
            l2 = nl2
            c2 = nc2
        # try add comments
        # l1, c1, l2, c2 = self._add_comments(lines, l1, c1, l2, c2)
        # one line
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
            if len(place.group(1)) <= c2:
                if (len(lines[l2]) - len(place.group(3))) <= c2:
                    del lines[l2]
                else:
                    lines[l2] = place.group(1) + lines[l2][c2:]
            for i in range(l2-1, l1, -1):
                del lines[i]
            place = re.search(r'^(\s*)(\S.*)$', lines[l1])
            if len(place.group(1)) >= c1:
                del lines[l1]
            else:
                lines[l1] = lines[l1][:c1]
        return True

    def _skip_tar(self, lines, l1, c1, l2, c2):
        """return new value possition witout tag, anchor or ref"""
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

    def _delete_value(self, root, lines, node):
        """Delete value and return start possition deleted value"""
        l1, c1, l2, c2 = node.span.start.line-1, node.span.start.column-1, \
            node.span.end.line-1, node.span.end.column-1
        l1, c1 = self._skip_tar(lines, l1, c1, l2, c2)
        # one line
        if l1 == l2:
            place = re.search(r'^(\s*)(\S.*\S)(\s*)$', lines[l1])
            if (len(place.group(1)) >= c1) and ((len(lines[l1]) - len(place.group(3))) <= c2):
                del lines[l1]
            else:
                lines[l1] = lines[l1][:c1] + lines[l1][c2:]
        else:
            # more lines
            place = re.search(r'^(\s*)(\S.*\S)(\s*)$', lines[l2])
            if len(place.group(1)) > c2:
                if (len(lines[l2]) - len(place.group(3))) <= c2:
                    del lines[l2]
                else:
                    lines[l2] = place.group(1) + lines[l2][c2:]
            for i in range(l2-1, l1, -1):
                del lines[i]
            place = re.search(r'^(\s*)(\S.*)$', lines[l1])
            if len(place.group(1)) >= c1:
                del lines[l1]
            else:
                lines[l1] = lines[l1][:c1]
        return l1, c1

    def _rewrite_first_ref(self, root, lines, anchors):
        """copy value from anchor node to first refference"""
        refs = {}
        self._find_all_ref(root, refs)
        refs_anchor = []
        refs_ref = []
        refs_remove = []
        for r in refs:
            if r in anchors and refs[r]['anchor'] is not None and len(refs[r]['ref']) > 0:
                ref_node = refs[r]['ref'][0]
                for ref in refs[r]['ref']:
                    if (ref_node.span.start.line > ref.span.start.line or
                            (ref_node.span.start.line == ref.span.start.line and
                             ref_node.span.start.column > ref.span.start.column)):
                        ref_node = ref
                added = False
                for i in range(0, len(refs_anchor)):
                    if (ref_node.span.start.line > refs_ref[i].span.start.line or
                            (ref_node.span.start.line == refs_ref[i].span.start.line and
                             ref_node.span.start.column > refs_ref[i].span.start.column)):
                        refs_anchor.insert(i, refs[r]['anchor'])
                        refs_ref.insert(i, ref_node)
                        refs_remove.insert(i, len(refs[r]['ref']) == 1)
                        added = True
                        break
                if not added:
                    refs_anchor.append(refs[r]['anchor'])
                    refs_ref.append(ref_node)
                    refs_remove.append(len(refs[r]['ref']) == 1)
        for i in range(0, len(refs_anchor)):
            self._copy_tree_from_anchor(lines, refs_anchor[i], refs_ref[i], refs_remove[i])

    def _copy_tree_from_anchor(self, lines, anchor_node, ref_node, remove_anchor=False):
        """Copy tree structure from anchor node to node with reference"""
        l1, c1, l2, c2 = anchor_node.span.start.line-1, anchor_node.span.start.column-1, \
            anchor_node.span.end.line-1, anchor_node.span.end.column-1
        l1, c1 = self._skip_tar(lines, l1, c1, l2, c2)
        hlpl1, hlpc1, l2, c2 = self._add_comments(lines, l1, c1, l2, c2)
        dl1, dc1, dl2, dc2 = self._get_node_pos(ref_node)
        intend = re.search(r'^(\s*)(\S.*)$', lines[dl1])
        intend = len(intend.group(1)) + 2
        add = self.StructureChanger.copy_structure(lines, l1, c1, l2, c2, intend)
        while dl1 <= dl2:
            ref = re.search(r'^(.*\*' + anchor_node.anchor.value + r')(.*)$', lines[dl1])
            if ref is not None:
                anchor = "&" + anchor_node.anchor.value
                if remove_anchor:
                    anchor = ""
                lines[dl1] = re.sub(r'\*' + anchor_node.anchor.value + r"\s+", anchor + " ",
                                    lines[dl1])
                lines[dl1] = re.sub(r'\*' + anchor_node.anchor.value + r"$", anchor, lines[dl1])
                if not ref.group(2).isspace() and len(ref.group(2)) > 0:
                    lines.insert(dl1+1, ref.group(2))
                    lines[dl1] = ref.group(1)
                for i in range(len(add)-1, -1, -1):
                    if len(add[i]) > 0 and not add[i].isspace():
                        lines.insert(dl1+1, add[i])
                break
            dl1 += 1

    @staticmethod
    def _next_spread(lines, line, column):
        """if next no-empty char is comma, return new possition"""
        if line < len(lines):
            return line, column
        old_line = line
        old_column = column
        while True:
            column += 1
            while len(lines[line]) <= column:
                column = 0
                line += 1
                if line < len(lines):
                    break
            if not lines[line][column].isspace():
                if lines[line][column] == ",":
                    return line, column
                break
        return old_line, old_column

    @staticmethod
    def _prev_spred(lines, line, column):
        """if previous no-empty char is comma, return new position"""
        old_line = line
        old_column = column
        while True:
            column -= 1
            while 0 > column:
                line -= 1
                if line < 0:
                    break
                column = len(lines[line])-1
            if not lines[line][column].isspace():
                if lines[line][column] == ",":
                    return line, column
                break
        return old_line, old_column
 
    def _get_type_place(self, lines, root, parent_node, place_forward=False):
        """
        Return type of placeing to root element

        1 - yaml array
        2 - yaml dict
        3 - comma befor
        4 - comma after
        """
        return 2

    def _move_key(self, root, lines, action):
        """Move key transformation"""
        try:
            parent1 = root.get_node_at_path(action['parameters']['destination_path'])
            raise TransformationFileFormatError(
                "Destination path (" + action['parameters']['destination_path'] + ") already exist")
        except:
            pass
        try:
            parent1 = re.search(r'^(.*)/([^/]*)$', action['parameters']['source_path'])
            node1 = root.get_node_at_path(action['parameters']['source_path'])
        except:
            return False
        try:
            parent2 = re.search(r'^(.*)/([^/]*)$', action['parameters']['destination_path'])
            node2 = root.get_node_at_path(parent2.group(1))
        except:
            raise TransformationFileFormatError(
                "Parent of destination path (" + action['parameters']['destination_path'] +
                ") must exist")
        sl1, sc1, sl2, sc2 = self._get_node_pos(node1)
        dl1, dc1, dl2, dc2 = self._get_node_pos(node2)
        if parent1.group(1) == parent2.group(1):
            # rename
            i = node1.key.span.start.line-1
            lines[i] = re.sub(parent1.group(2) + r"\s*:", parent2.group(2) + ":", lines[i])
            return True
        if node2.implementation != DataNode.Implementation.mapping:
            raise TransformationFileFormatError(
                "Parent of destination path (" + action['parameters']['destination_path'] +
                ") must be abstract record")
        intendation1 = re.search(r'^(\s*)(\S.*)$', lines[dl1])
        intendation1 = len(intendation1.group(1)) + 2
        sl1, sc1, sl2, sc2 = self._add_comments(lines, sl1, sc1, sl2, sc2)
        add = StructureChanger.copy_structure(lines, sl1, sc1, sl2, sc2, intendation1)
        # rename key
        i = node1.key.span.start.line - sl1 - 1
        add[i] = re.sub(parent1.group(2) + r"\s*:", parent2.group(2) + ":", add[i])
        if sl2 < dl1 or (sl2 == dl1 and sc2 < dc1):
            # source before dest, first copy
            intendation2 = re.search(r'^(\s*)(\S.*)$', lines[dl2])
            for i in range(len(add)-1, -1, -1):
                if len(intendation2.group(1)) < dc2:
                    # to end file
                    lines.insert(dl2+1, add[i])
                else:
                    lines.insert(dl2, add[i])
            action['parameters']['path'] = action['parameters']['source_path']
            self._delete_key(root, lines, action)
        elif dl2 < sl1 or (dl2 == sl1 and dl2 < sc1):
            # source after dest, first delete
            action['parameters']['path'] = action['parameters']['source_path']
            self._delete_key(root, lines, action)
            intendation2 = re.search(r'^(\s*)(\S.*)$', lines[dl2])
            for i in range(len(add)-1, -1, -1):
                if len(intendation2.group(1)) < dc2:
                    # to end file
                    lines.insert(dl2+1, add[i])
                else:
                    lines.insert(dl2, add[i])
        else:
            raise TransformationFileFormatError(
                "Destination block (" + action['parameters']['source_path'] +
                ") and source block (" + action['parameters']['destination_path'] +
                " is overlapped")
        return True
        
    def _add_array(self, root, lines, action):
        """Move key transformation"""
        try:
            parent2 = root.get_node_at_path(action['parameters']['addition_path'])
        except:
            return False
        if parent2.implementation == DataNode.Implementation.sequence:
            raise TransformationFileFormatError(
                    "Specified addition path (" + action['parameters']['path'] + \
                    ") is not array type node." )
        try:
            parent1 = root.get_node_at_path(action['parameters']['source_path'])
        except:
            return False
        if parent1.implementation == DataNode.Implementation.sequence:
            raise TransformationFileFormatError(
                    "Specified source path (" + action['parameters']['path'] + \
                    ") is not array type node." )        
        if parent2 == parent1:
            raise TransformationFileFormatError(
                "Source and addition paths must be different (" + 
                action['parameters']['source_path'] + ")")
        sl1, sc1, sl2, sc2 = self._get_value_pos(parent1)
        sl2, sc2 = self._fix_end(self, lines, sl1, sc1, sl2, sc2 )
        al1, ac1, al2, ac2 = self._get_value_pos(parent2)
        al2, ac2 = self._fix_end(self, lines, al1, ac1, al2, ac2 )
        if (al1>=sl1 and sl2>=al2) or (sl1>=al1 and al2>=sl2):
            raise TransformationFileFormatError(
                "Source and addition nodes can't contains each other (" + 
                action['parameters']['source_path'] + ")")
        
        intendation1 = re.search(r'^(\s*)(\S.*)$', lines[sl1])
        sl1, sc1, sl2, sc2 = self._add_comments(lines, al1, ac1, al2, ac2)
        add = StructureChanger.copy_structure(lines, al1, ac1, al2, ac2, intendation1)

        if al2 < sl1 or (al2 == sl1 and al2 < sc1):
            # source after addition, first delete
            action['parameters']['path'] = action['parameters']['source_path']
            self._delete_key(root, lines, action)
        self._add_comma(lines, sl2, sc2 )
        for i in range(len(add)-1, -1, -1):
            lines.insert(sl2+1, add[i])
        if not(al2 < sl1 or (al2 == sl1 and al2 < sc1)):
            action['parameters']['path'] = action['parameters']['source_path']
            self._delete_key(root, lines, action)
        return True

    def _rename_type(self, root, lines, action):
        """Rename type transformation"""
        try:
            node = root.get_node_at_path(action['parameters']['path'])
        except:
            return False
        old = '!' + action['parameters']['old_name'] 
        new = '!' + action['parameters']['new_name']
        l1, c1, l2, c2 = self._get_node_pos(node)
        return self._replace(lines, new,  old,  l1, c1, l2, c2 )

    def _fix_end(self, lines, l1, c1, l2, c2 ):
        """If end of node is empty  on next line, end is move to end of preceding line"""
        if c2==0 or lines[l2][:c2].isspace():
            if l1 < l2:
                return l2-1, len(lines[l2-1])
        return l2, c2
        
    def _add_comma(self, lines, l2, c2 ):
        """add comma to the end of array"""
        sep = re.search(r'^(\s*)-(\s+)$', lines[l2])
        if sep is not None:
            return
        if c2 < len(lines[l2]) and not lines[l2][c2:].isspace():
           add =  lines[l2][c2:]
           lines[l2] = lines[l2][:c2]
           lines.insert(l2+1, add)
        lines[l2] += ','   

    def _replace(self, lines, new,  old,  l1, c1, l2, c2 ):
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
        
    def _change_value(self, root, lines, action):
        """Rename type transformation"""
        try:
            node = root.get_node_at_path(action['parameters']['path'])
        except:
            return False
        if node.implementation == DataNode.Implementation.scalar:
            raise TransformationFileFormatError(
                    "Specified path (" + action['parameters']['path'] + ") is not scalar type node." )
        old = '!' + action['parameters']['old_value'] 
        new = '!' + action['parameters']['new_value']
        l1, c1, l2, c2 =  self._get_value_pos(node)
        return self._replace(lines, new,  old,  l1, c1, l2, c2 )

    @staticmethod
    def _get_node_pos(node):
        """return position of node in file"""
        return node.start.line-1, node.start.column-1, node.end.line-1, node.end.column-1
    
    @staticmethod
    def _get_value_pos(node):
        """return value position in file of set node """
        return node.span.start.line-1, node.span.start.column-1, \
            node.span.end.line-1, node.span.end.column-1

    @staticmethod
    def _add_comments(lines, l1, c1, l2, c2):
        """Try find comments before node and add it to node"""
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


class TransformationFileFormatError(Exception):
    """Represents an error in transformation file"""

    def __init__(self, msg):
        super(TransformationFileFormatError, self).__init__(msg)
