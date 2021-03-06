import sys
import os
import logging
import traceback
import time
import json

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))))), "src"))

from JobPanel.backend.service_base import ServiceBase, LongRequest


class TService(ServiceBase):
    def _do_work(self):
        if time.time() > self.start_time + 60:
            self._closing = True

    @LongRequest
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
        input_file = "t_service.conf"
        with open(input_file, "r") as f:
            config = json.load(f)
        bs = TService(config)
        bs.run()
    except:
        logging.error("Uncatch exception:\n" + "".join(traceback.format_exception(*sys.exc_info())))
        raise
