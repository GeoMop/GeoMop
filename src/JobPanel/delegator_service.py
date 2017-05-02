
import backend.async_repeater as ar
from backend import service_base
import sys
import logging
import time
import json
import traceback

class Delegator(service_base.ServiceBase):
    """
    """
    def __init__(self, config):
        service_base.ServiceBase.__init__(self, config)
        #self.closing = False


    # def run(self):
    #     self.repeater.run(0.1)  # run for some time
    #     logging.info("After run")
    #     while not self.closing:
    #         logging.info("Loop")
    #         time.sleep(1)
    #         self._process_answers()
    #         self._process_requests()
    #     self.repeater.close()

    """ Delegator requests. """


    """
    Delegator requests. (WIP)
    """
    def request_start_service(self, executor_config):
        executor = JsonData.make_instance(executor_config)
        executor.exec()


    def request_kill_service(self, executor_config):
        executor = JsonData.make_instance(executor_config)
        executor.kill()


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

