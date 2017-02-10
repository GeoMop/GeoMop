
import async_repeater as ar
import service_base
import sys

class BackendService(service_base.ServiceBase):
    def __init__(self, service_address):
        service_base.ServiceBase.__init__(self, service_address, 45847)
        self.closing = False


    def run(self):
        while not self.closing:

            self.repeater.run(0.1)  # run for some time
            print("After run")
            self.process_answers()
            self.process_requests()
        self.repeater.close()


##########
# Main body
##########

log = open('backlog',"w")

address = sys.argv[1]
port_output_file = sys.argv[2]
bs=BackendService(address)
log.write("port file: %s\n"%(port_output_file))
print("port: %d\n"%(bs.get_listen_port())  )
with open(port_output_file, "a") as f:
    log.write("port: %d\n" % (bs.get_listen_port()))
    f.write(" %d"%(bs.get_listen_port()))
log.close()
sys.stdout.flush()

bs.run()
