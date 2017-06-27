import sys
import os
import logging
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from backend import service_base


class Backend(service_base.ServiceBase):
    """
    """
    config_file_name = "backend_service.conf"

    def __init__(self, config):
        service_base.ServiceBase.__init__(self, config)

    """ Backend requests. """


##########
# Main body
##########


logging.basicConfig(filename='backend.log', filemode="w",
                    format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    level=logging.INFO)


try:
    bs = Backend({"repeater_address": [int(sys.argv[1])],
                  "parent_address": [sys.argv[2], int(sys.argv[3])]})
    bs.run()
except:
    logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
    raise
