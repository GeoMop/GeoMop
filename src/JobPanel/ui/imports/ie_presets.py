import yaml
import os
import copy

class IE:
    """
    Import and export of defined simple data.
    """
    items = []
    default_items = {}
    
    def __init__(self, file):
        self.file = file

    def import_(self, temp_item):
        """Import structure"""
        if not os.path.isfile(self.file):
            raise Exception("Import file is not exist")
        datas = {}
        yaml_file = open(self.file, 'r')
        new_datas = yaml.load(yaml_file)
        for key in new_datas:
            new_data = new_datas[key]
            data =  copy.deepcopy(temp_item)
            for attr in self.items:
                if attr in new_data:
                    setattr(data, attr, new_data[attr])
                elif(attr in self.default_items):
                    setattr(data, attr, self.default_items[attr])
                else:
                    yaml_file.close()
                    raise Exception("Imported attribute {0} is not exist".format(attr))            
            for attr in self.default_items:
                if self.default_items not in self.items:
                    setattr(data, attr, self.default_items[attr])
            datas[key] = data 
        yaml_file.close()
        return datas
        
    def export_(self, datas):
        """export structure"""
        export_data = {}        
        for key in datas:
            data = datas[key]
            export_data_item = {}
            for attr in self.items:
                if hasattr(data, attr):
                    export_data_item[attr] = getattr(data, attr)
                else:
                    raise Exception("Exported attribute {0} is not exist".format(attr))
            export_data[key] = export_data_item
        yaml_file = open(self.file, 'w')
        yaml.dump(export_data, yaml_file)
        yaml_file.close()
        
    @classmethod    
    def cmp(cls, item1, item2):
        """export structure"""
        for attr in cls.items:
            if not hasattr(item1, attr) or not hasattr(item2, attr):
                return False
            if getattr(item1, attr) != getattr(item2, attr):
               return False
        return True

class IEWorkspace(IE):
    items = ["pc"]
    default_items = {}

class IEEnv(IE):
    items = ["cli_params", "flow_path", "module_add", "name", "pbs_params", 
        "python_exec", "scl_enable_exec"]
    default_items = {}
    
class IEPbs(IE):
    items = ["infiniband", "pbs_system", "memory", "name", "nodes", "ppn", "queue", "walltime"]
    default_items = {}
    
class IESsh(IE):
    items = ["env", "host", "name", "pbs_system", "port", "remote_dir", "uid"]
    default_items = {"key":"", "pwd":"", "to_pc": False, "to_remote": False, 
    "use_tunneling": False}
        
class IERes(IE):
    items = ["j_execution_type", "j_pbs_preset", "j_remote_execution_type", 
        "j_ssh_preset", "mj_execution_type", "mj_pbs_preset", 
        "mj_remote_execution_type", "mj_ssh_preset", "name"]
    default_items = {}

class IEMj(IE):
    items = ["analysis", "log_level", "name", "number_of_processes", "resource_preset", "deleted_remote"]
    default_items = {}
    
    def export_(self, datas):
        only_presets = {}
        for key in datas:
            only_presets[key] = datas[key].preset
        super(IEMj, self). export_(only_presets)
        
    def import_(self, temp_item):
        presets_temp_item = temp_item.preset
        datas = super(IEMj, self). import_(presets_temp_item)
        data = {}
        for key in datas:
            data[key] =  copy.deepcopy(temp_item)
            data[key].preset = datas[key]
        return data
        
    @classmethod    
    def cmp(cls, item1, item2):        
        """export structure"""
        return super(IEMj, cls). export_(item1.preset, item2.preset)
