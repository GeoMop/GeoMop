import sys
import os
import logging
import traceback
import time

#sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from backend import service_base


class TService(service_base.ServiceBase):
    @service_base.LongRequest
    def request_long(self, data):
        time.sleep(2)
        return True

    def request_error(self, data):
        a = 1 / 0
        return a


if __name__ == "__main__":
    logging.basicConfig(filename='t_service.log', filemode="w",
                        format='%(asctime)s %(levelname)-8s %(name)-12s %(message)s',
                        level=logging.INFO)

    try:
        bs = TService({"repeater_address": [int(sys.argv[1])],
                       "parent_address": [sys.argv[2], int(sys.argv[3])]})
        bs.run()
    except:
        logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
        raise
