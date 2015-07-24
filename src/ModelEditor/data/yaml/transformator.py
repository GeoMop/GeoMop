import json

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
            raise TransformationFileFormatError("Parameter " + name +" for action type'" 
                + act_type + "' si required" + " (action: " + str(line) +")")
        if  dict[name] is None or dict[name] == "":
            raise TransformationFileFormatError("Parameter " + name +" for action type'" 
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

    def transform(self, root, yaml):
        """transform yaml file"""
        for action in self._transformation['actions']:
            if action['action'] == "delete-key":
                self._delete_key(root, yaml,  action)
            elif action['action'] == "move-key":
                self._move_key(root, yaml,  action)
            elif action['action'] == "rename-type":
                self._rename_type(root, yaml,  action)
      
    def _delete_key(self, root, yaml,  action):
        """Delete key transformation"""
        
    def _move_key(self, root, yaml,  action):
        """Delete key transformation"""
        
    def _rename_type(self, root, yaml,  action):
        """Delete key transformation"""

class TransformationFileFormatError(Exception):
    """Represents an error in transformation file"""
    
    def __init__(self, msg):
        super(TransformationFileFormatError, self).__init__(msg)
        
