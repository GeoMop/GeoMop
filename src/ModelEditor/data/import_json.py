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

def parse_con(con):
    """
    Parses a configuration file of Flow123d in .con format with given filename.
    If the input file includes references, they are resolved and represented
    by actual python references in the output.

    Returns the yaml text structure.
    """
    data = _decode_con(con)
    data =_resolve_references(data)
    data = yaml.dump(data, default_flow_style=False, indent=4)
    return data
    
def _resolve_references(data):
    """
    Resolves references in data. Replaces REF keys with actual Python
    references.
    """
#    refs = _extract_references(data)
#    root = DataNode(data)
#    while len(refs) > 0:
#        length = len(refs)
#        for path, ref_path in copy(refs).items():
#            try:
#                node = root.get(path)
#                if ref_path.startswith('/'):  # absolute ref
#                    node.ref = root.get(ref_path)
#                else:  # relative ref
#                    node.ref = node.get(ref_path)
#            except LookupError:
#                continue
#            else: del refs[path]
#        if length == len(refs):
#            # no reference removed -> impossible to resolve references
#            raise RefError("Can not resolve references.")
#    return root

    return data

def _decode_con(con):
    """Reads .con format and returns read data in form of dicts and lists."""
    pattern = re.compile(r"\s?=\s?")  # TODO can I replace = simply like this?
    con = pattern.sub(':', con)
    return demjson.decode(con)

def _extract_references(json):
    """
    Crawl through the data and find all REF keys.

    Returns a dictionary of their locations and where they point.
    """
    def crawl(data, path):
        if isinstance(data, dict):
            try:
                ref_path = data['REF']
            except KeyError:
                pass
            else:
                refs[path] = ref_path
                del data['REF']
            # crawl for all keys
            for key, value in data.items():
                crawl(value, '{path}/{key}'.format(path=path, key=key))
        elif isinstance(data, list):
            # crawl for all records
            for i, item in enumerate(data):
                crawl(item, '{path}/{key}'.format(path=path, key=i))

    refs = {}
    crawl(json, '')
    return refs
