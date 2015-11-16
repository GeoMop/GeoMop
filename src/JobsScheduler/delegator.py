"""delegator test file"""
import sys
import logging

sys.path.insert(1, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(2, './twoparty/enum')

import data.communicator_conf as comconf
import communication.installation as inst
from communication import Communicator

logger = logging.getLogger("Remote")

if len(sys.argv)<2:
    raise Exception('Multijob name as application parameter is require')
mj_id = None
mj_name = sys.argv[1]
if len(sys.argv) > 2 and sys.argv[2] != "&":
    mj_id = sys.argv[2]

# Load from json file
com_conf = comconf.CommunicatorConfig(mj_name)
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

if __name__ != "delegator":
    # no doc generation
    comunicator.run()
comunicator.close()
logger.info("Application " + comunicator.communicator_name + " is stopped")
