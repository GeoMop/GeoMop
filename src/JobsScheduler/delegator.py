"""delegator test file"""

import sys
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import logging
import data.communicator_conf as comconf
from communication import Communicator

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv)>2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

ccom = comconf.CommunicatorConfig(mj_name)
ccom.communicator_name = "delegator"
ccom.next_communicator = "mj_service"
ccom.log_level = logging.DEBUG
ccom.input_type = comconf.InputCommType.std
#ccom.output_type = comconf.OutputCommType.pbs
#ccom.pbs = comconf.PbsConfig()
#ccom.python_exec = "/opt/python/bin/python3.3"
#ccom.pbs.with_socket = True
#ccom.pbs.name = "mj_service"
ccom.output_type = comconf.OutputCommType.exec_

comunicator = Communicator(ccom, mj_id)

logging.error("Name: " + __name__)

if __name__ != "delegator":
    # no doc generation
    comunicator.run()
comunicator.close()


