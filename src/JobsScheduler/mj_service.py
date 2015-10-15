"""mj_service test file"""

import sys
import logging
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')
    
import data.communicator_conf as comconf
from communication import JobsCommunicator

def  mj_action_function_before(message):
    """before action function"""
    return comunicator.standart_action_function_before(message)
    
def  mj_action_function_after(message,  response):
    """before action function"""
    return comunicator.standart_action_function_after(message,  response)

i = 0
def  mj_idle_function():
    """This function will be call, if meesage is not receive in run function."""
    global i
    i += 1
    if i == 1:
        comunicator.add_job("test1", None)
    if i == 2:
        comunicator.add_job("test2", None)

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "mj_service"
ccom.next_communicator = "job"
ccom.log_level = logging.DEBUG
#ccom.input_type = comconf.InputCommType.pbs
ccom.input_type = comconf.InputCommType.socket
ccom.output_type = comconf.OutputCommType.exec_
#ccom.output_type = comconf.OutputCommType.pbs
#ccom.pbs = comconf.PbsConfig()
#ccom.python_exec = "/opt/python/bin/python3.3"
#ccom.pbs.with_socket = False
#ccom.pbs.name = "test"
comunicator = JobsCommunicator(ccom, None, mj_action_function_before, mj_action_function_after, mj_idle_function)
if __name__ != "mj_service":
    # no doc generation
    comunicator.run()
comunicator.close()

