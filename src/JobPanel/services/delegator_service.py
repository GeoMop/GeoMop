import sys
import os
import logging
import time
import json
import traceback

sys.path.append(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])

import backend.async_repeater as ar
from backend import service_base
from backend.json_data import JsonData, ClassFactory
from backend._executor import ProcessExec, ProcessPBS, ProcessDocker


class Delegator(service_base.ServiceBase):
    """
    """
    def __init__(self, config):
        service_base.ServiceBase.__init__(self, config)

        self._process_class_factory = ClassFactory([ProcessExec, ProcessPBS, ProcessDocker])

    """ Delegator requests. """

    def request_process_start(self, process_config):
        logging.info("request_process_start(process_config: {})".format(process_config))
        executor = self._process_class_factory.make_instance(process_config)
        return executor.start()

    def request_process_status(self, process_config):
        executor = self._process_class_factory.make_instance(process_config)
        return executor.get_status()


    def request_process_kill(self, process_config):
        executor = self._process_class_factory.make_instance(process_config)
        return executor.kill()


    def request_clean_workspace(self):
        pass

##########
# Main body
##########



logging.basicConfig(filename='delegator.log', filemode="w",
                    format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    level=logging.INFO)


try:
    bs = Delegator({"repeater_address": [int(sys.argv[1])],
                    "parent_address": [sys.argv[2], int(sys.argv[3])]})
    bs.run()
except:
    #logging.error("{}: {}".format(sys.exc_info()[0].__name__, sys.exc_info()[1]))
    logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
    raise


#print(bs.get_listen_port())


# address = json.loads(sys.argv[1])
# logging.info("addr: %s"%(str(address)))
# port_output_file = sys.argv[2]
# bs=Delegator(address)
# logging.info("port file: %s\n"%(port_output_file))
# print("port: %d\n"%(bs.get_listen_port())  )
# with open(port_output_file, "a") as f:
#     logging.info("port: %d\n" % (bs.get_listen_port()))
#     f.write(" %d"%(bs.get_listen_port()))


#sys.stdout.flush()


# TODO:
# use only logging, check that loggig flush
# try to proof ping
#

