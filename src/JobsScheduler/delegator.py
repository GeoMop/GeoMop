"""delegator test file"""

import sys
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import logging
import data.communicator_conf as comconf
from communication import Communicator

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "delegator"
ccom.next_communicator = "multijob"
ccom.log_level = logging.DEBUG
ccom.input_type = comconf.InputCommType.std
ccom.output_type = comconf.OutputCommType.pbs
ccom.pbs = comconf.PbsConfig()
ccom.python_exec = "/opt/python/bin/python3.3"
ccom.pbs.with_socket = True
ccom.pbs.name = "mj"

comunicator = Communicator(ccom)

comunicator.run()
comunicator.close()


