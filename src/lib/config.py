"""
Library for work with state of GeoMops applications
"""

import os
import yaml

__config_dir__=os.path.join(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0], "config")
try:
    if( not os.path.isdir(__config_dir__)):
        os.makedirs(__config_dir__)
except:
    raise Exception('Cannot create config directory')
 
def get_config_file(name):
    """
    Get config object from file Name.cfg in config directory
    
    return: Config object or None (if file not exist)
    """
    file_name=os.path.join(__config_dir__, name+'.yaml')
    try:
        yaml_file = open(file_name, 'r')
    except (FileNotFoundError, IOError):
        return None
    config=yaml.load(yaml_file)
    yaml_file.close()
    return config
    
def save_config_file(name,  config):
    """Save config object to file Name.cfg in config directory"""    
    file_name=os.path.join(__config_dir__, name+'.yaml')
    yaml_file = open(file_name, 'w')
    yaml.dump(config, yaml_file)
    yaml_file.close()

def delete_config_file(name):
    """
    Delete config file Name.cfg from config directory
     """
    file_name=os.path.join(__config_dir__, name+'.yaml')
    try:
        os.remove(file_name)
    except (FileNotFoundError):
        return
