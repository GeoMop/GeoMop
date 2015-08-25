"""delegator test file"""

import sys
sys.path.insert(1, './twoparty/pexpect')

import logging
import data.communicator_conf as comconf
from communication.communicator import Communicator

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "delegator"
ccom.next_communicator = "multijob"
ccom.log_level = logging.DEBUG
ccom.input_type = comconf.InputCommType.std
ccom.output_type = comconf.OutputCommType.exec_
comunicator = Communicator(ccom)

comunicator.run()
comunicator.close()


