"""
Library for work with state of GeoMops applications
"""

import os
import pickle

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
    file_name=os.path.join(__config_dir__, name+'.cfg')
    try:
        pkl_file = open(file_name, 'rb')
    except (FileNotFoundError, IOError):
        return None
    config=pickle.load(pkl_file)
    pkl_file.close()
    return config
    
def save_config_file(name,  config):
    """Save config object to file Name.cfg in config directory"""    
    file_name=os.path.join(__config_dir__, name+'.cfg')
    pkl_file = open(file_name, 'wb')
    pickle.dump(config, pkl_file)
    pkl_file.close()

def delete_config_file(name):
    """
    Delete config file Name.cfg from config directory
     """
    file_name=os.path.join(__config_dir__, name+'.cfg')
    try:
        os.remove(file_name)
    except (FileNotFoundError):
        return
