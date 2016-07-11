"""delegator test file"""
import sys
import logging
import os

sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import data.communicator_conf as comconf
import communication.installation as inst
from communication import Communicator

import signal
def end_handler(signal, frame):
    comunicator.close()
        
signal.signal(signal.SIGINT, end_handler)

logger = logging.getLogger("Remote")

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

# Load from json file
com_conf = comconf.CommunicatorConfig()
if os.path.isdir(mj_name) and  os.path.isabs(mj_name):
    directory = os.path.join(mj_name, inst.__conf_dir__)
else:
    directory = inst.Installation.get_config_dir_static(mj_name)
path = comconf.CommunicatorConfigService.get_file_path(
    directory, comconf.CommType.delegator.value)
try:
    with open(path, "r") as json_file:
        comconf.CommunicatorConfigService.load_file(json_file, com_conf)
except Exception as error:
    logger.error(error)
    raise error

comunicator = Communicator(com_conf, mj_id)
logger.debug("Mj config dir {0}({1})".format(path, mj_name))

if __name__ != "delegator":
    # no doc generation
    try:
        comunicator.run()
    except Exception as err:
        comunicator.close()
        logger.info("Application stop for uncatch error:" + str(err)) 
        sys.exit(1)
comunicator.close()
logger.info("Application " + comunicator.communicator_name + " is stopped")
