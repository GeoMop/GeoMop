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

def parse_con(con):
    """
    Parses a configuration file of Flow123d in .con format with given filename.

    Returns the yaml text structure.
    """
    data = _decode_con(con)
    data = yaml.dump(data, default_flow_style=False, indent=2)
    return data
    
def _decode_con(con):
    """Reads .con format and returns read data in form of dicts and lists."""
    pattern = re.compile(r"\s?=\s?")  # TODO can I replace = simply like this?
    con = pattern.sub(':', con)
    return demjson.decode(con)
    
def fix_tags(yaml, root):
    """Replase TYPE and refferences by tags"""
    lines = yaml.splitlines(False)
    del_lines = traverse_nodes(root, lines)
    new_lines = []
    for i in range(0, len(lines)):
        if i not in del_lines:
            new_lines.append(lines[i])
    return "\n".join(new_lines)
 
def traverse_nodes(node, lines):
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
                lines[node.key.span.start.line-1] += " !ref " + child.value
            else:
                if isinstance(child, dn.CompositeNode):
                    del_lines.extend(traverse_nodes(child, lines))
    return del_lines
    
    
    
    
    
