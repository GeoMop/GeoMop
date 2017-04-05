
import async_repeater as ar
import service_base
import sys
import logging
import time
import json

class Delegator(service_base.ServiceBase):
    def __init__(self, service_address):
        service_base.ServiceBase.__init__(self, service_address, 45847)
        self.closing = False


    def run(self):
        self.repeater.run(0.1)  # run for some time
        logging.info("After run")
        while not self.closing:
            logging.info("Loop")
            time.sleep(1)
            self.process_answers()
            self.process_requests()
        self.repeater.close()


##########
# Main body
##########

# print("ahoj\n")
# time.sleep(60)
# sys.exit(0)


logging.basicConfig(filename='backlog',  filemode="w", level=logging.DEBUG)


bs=Delegator(0)
print(bs.get_listen_port())


# address = json.loads(sys.argv[1])
# logging.info("addr: %s"%(str(address)))
# port_output_file = sys.argv[2]
# bs=Delegator(address)
# logging.info("port file: %s\n"%(port_output_file))
# print("port: %d\n"%(bs.get_listen_port())  )
# with open(port_output_file, "a") as f:
#     logging.info("port: %d\n" % (bs.get_listen_port()))
#     f.write(" %d"%(bs.get_listen_port()))


sys.stdout.flush()

bs.run()

# TODO:
# use only logging, check that loggig flush
# try to proof ping
#

