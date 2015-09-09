"""
Library for work with state of GeoMops applications
"""

import os
import yaml

__config_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "config")

try:
    if not os.path.isdir(__config_dir__):
        os.makedirs(__config_dir__)
except:
    raise Exception('Cannot create config directory')

def get_config_file(name, dir = None):
    """
    Get config object from file Name.cfg in config directory

    return: Config object or None (if file not exist)
    """
    if dir is not None:
        directory = os.path.join(__config_dir__, dir)
        if not os.path.isdir(directory):
            return None
    else:
        directory = __config_dir__
    file_name = os.path.join( directory, name+'.yaml')
    try:
        yaml_file = open(file_name, 'r')
    except (FileNotFoundError, IOError):
        return None
    config = yaml.load(yaml_file)
    yaml_file.close()
    return config

def save_config_file(name, config, dir = None):
    """Save config object to file Name.cfg in config directory"""
    if dir is not None:
        directory = os.path.join(__config_dir__, dir)
        try:
            if not os.path.isdir(directory):
                os.makedirs(directory)
        except:
            raise Exception('Cannot create config directory: ' + dir)        
    else:
        directory = __config_dir__
    file_name = os.path.join(directory, name+'.yaml')
    yaml_file = open(file_name, 'w')
    yaml.dump(config, yaml_file)
    yaml_file.close()

def delete_config_file(name, dir = None):
    """
    Delete config file Name.cfg from config directory
     """
    if dir is not None:
        directory = os.path.join(__config_dir__, dir)
        if not os.path.isdir(directory):
            return
    else:
        directory = __config_dir__
    file_name = os.path.join(directory, name+'.yaml')
    try:
        os.remove(file_name)
    except  (RuntimeError, IOError):
        return
