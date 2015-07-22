import json

class Transformator:
    """Transform yaml file to new version"""
    
    def __init__(self,  transform_file):
        """init"""
        self._transformation = json.load(transform_file)
        "parsed json transformation file"
        
    def old_version(self):
        """return version of yaml document befor transformation"""
        
    def new_version(self):
        """return version of yaml document after transformation"""
        
    def description(self):
        """return transformation description"""

    def name(self):
        """return transformation name"""
        
    def transform(self, root, yaml):
        """transform yaml file"""
