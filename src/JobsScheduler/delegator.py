import sys
sys.path.insert(1, './twoparty/pexpect')

import data.communicator_conf as comconf
from communication.comunicator import Communicator

ccom = comconf.CommunicatorConfig()
ccom.input_type = comconf.InputCommType.std
comunicator = Communicator(ccom)
comunicator.run()

def  standart_action_funcion(message):
    return False, True, None
