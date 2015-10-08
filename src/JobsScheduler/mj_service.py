"""mj_service test file"""

import sys
import logging
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')
    
import data.communicator_conf as comconf
from communication import JobsCommunicator

def  mj_action_funcion_before(message):
    """before action function"""
    return comunicator.standart_action_funcion_before(message)
    
def  mj_action_funcion_after(message,  response):
    """before action function"""
    return comunicator.standart_action_funcion_after(message,  response)

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "mj_service"
ccom.log_level = logging.DEBUG
#ccom.input_type = comconf.InputCommType.pbs
ccom.input_type = comconf.InputCommType.socket
comunicator = JobsCommunicator(ccom, None, mj_action_funcion_before, mj_action_funcion_after)
if __name__ != "mj_service":
    # no doc generation
    comunicator.run()
comunicator.close()

