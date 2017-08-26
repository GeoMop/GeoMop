import sys
import os
import logging
import traceback
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

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


logging.basicConfig(filename='backend_service.log', filemode="w",
                    format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                    level=logging.INFO)


try:
    input_file = "backend_service.conf"
    with open(input_file, "r") as f:
        config = json.load(f)
    bs = Backend(config)
    bs.run()
except:
    logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
    raise
