import sys
import os
import logging
import traceback

sys.path.append(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])

from backend import service_base


class Backend(service_base.ServiceBase):
    """
    """
    def __init__(self, config):
        service_base.ServiceBase.__init__(self, config)

    """ Backend requests. """


##########
# Main body
##########


logging.basicConfig(filename='backend.log', filemode="w",
                    format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    level=logging.INFO)


import time
time.sleep(100)
try:
    bs = Backend({"repeater_address": [int(sys.argv[1])],
                  "parent_address": [sys.argv[2], int(sys.argv[3])]})
    bs.run()
except:
    logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
    raise
