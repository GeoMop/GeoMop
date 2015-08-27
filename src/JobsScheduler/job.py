import sys
sys.path.insert(1, './twoparty/pexpect')

import time
import logging
import data.communicator_conf as comconf
from communication.communicator import Communicator

ccom = comconf.CommunicatorConfig()
ccom.communicator_name = "job"
ccom.log_level = logging.INFO
comunicator = Communicator(ccom)
logging.info("Start")
for i in range(0, 30):
    time.sleep(30)
    logging.info( "time: " + str(i*30+30) + "s")
logging.info( "End" )   
