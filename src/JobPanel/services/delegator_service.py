import sys
import os
import logging
import time
import json
import traceback
import psutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from backend import service_base


class Delegator(service_base.ServiceBase):
    """
    """

    def __init__(self, config):
        service_base.ServiceBase.__init__(self, config)

    """ Delegator requests. """

    def request_clean_workspace(self):
        pass

##########
# Main body
##########


if __name__ == "__main__":
    p = psutil.Process()
    filename = "{}_{}.log".format(time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(p.create_time())), p.pid)
    logging.basicConfig(filename=filename, filemode="w",
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

