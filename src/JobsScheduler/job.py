import sys
sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import time
import logging
import subprocess
import data.communicator_conf as comconf
from communication import Communicator
from  communication.installation import  Installation

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv)>2  and sys.argv[2] != "&":
    mj_id = sys.argv[2]

ccom = comconf.CommunicatorConfig(mj_name)
ccom.communicator_name = "job"
ccom.log_level = logging.INFO
ccom.python_exec = "/opt/python/bin/python3.3"

comunicator = Communicator(ccom, mj_id)
logging.info("Start")

process = subprocess.Popen([ccom.python_exec,"test_task.py", 
    Installation.get_result_dir_static(ccom.mj_name)], stderr=subprocess.PIPE)
return_code = process.poll()
if return_code is not None:
    out = process.stderr.readline()
    logging.error("Can not start test task (return code: " + str(return_code) + 
        ",stderr:" + out + ")")

time.sleep(5)
out = process.stderr.readline()
if out is not None and len(out)>0 and not out.isspace():
    logging.warning("Message in stderr:" + out)

if __name__ != "job":
    for i in range(0, 30):
        time.sleep(30)
        logging.info( "time: " + str(i*30+30) + "s")
logging.info( "End" )   
