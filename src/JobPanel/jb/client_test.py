import subprocess
import service_base
import os
import re
import logging
import time


"""
MJ and Jb states:
see class TaskStatus in data/states.py

List of requests:
- ping; cl to bk, cl to mj, mj to jb
- start mj, jb; cl to bk (long)
- stop mj, jb; cl to mj, mj to jb
- kill mj, jb; cl to bk, ( possible role of delegator to kill mj and jb)
- reconnect mj; cl to bk
- get analysis progress; completion of actions, prograss of actions

- get analysis action summary (over socket), include big data list
- get analysis action data (download);


Aim:
Proof of concept of async messaging:
- start backend (start in docker)
- connect to beckend, ping
- start mj back on origin machine (start by exec over ssh)
- ping mj
- stop mj
- stop backend
"""

class BackendProxy:
    def __init__(self):
        self.docker_process = None
        host_geomop_root = "/home/jb/workspace/GeoMop/src/JobPanel"
        guest_geomop_root = "/home/geomop/root"
        host_workspace = "/home/jb"
        guest_workspace="/home/geomop/workspace"
        docker_image = "geomop:backend"
        backend_service = guest_geomop_root + "/" + "jb/backend_service.py"
        id_file="__backend_cont_id.txt"

        host_id_file=host_workspace + "/" + id_file
        guest_id_file=guest_workspace + "/" + id_file
        try:
            os.remove(host_id_file)
        except:
            pass

        logging.info("Starting backend ...\n")
        self.docker_process = subprocess.Popen(
            ['docker', 'run', '--rm',
             '--cidfile=' + host_id_file,
             # mount dires
             '-v', "%s:%s"% (host_geomop_root, guest_geomop_root),
             '-v', "%s:%s" % (host_workspace, guest_workspace),
             # work dir
             '-w', guest_workspace,
             docker_image, "python3",
             backend_service, "[0]", id_file], stdout = subprocess.PIPE)

        # get listen port from stdout
        while True:
            line=self.docker_process.stdout.readline()
            if line:
                l=line.decode().split()
                if (len(l) == 2 and l[0] == 'port:'):
                    self.backend_port = int(l[1])
                else:
                    raise ValueError("Wrong format of backend output, can not get port.")
                break
        # get docker hash via file
        with open(host_id_file, 'rt') as f:
            self.docker_hash = f.readline().split()[0]
        os.remove(host_id_file)

        output = subprocess.check_output([ 'docker', 'inspect',
                          '--format=\'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\'',
                          self.docker_hash])

        output = output.decode().strip()
        if output.startswith("'") and output.endswith("'"):
            backend_docker_ip = output[1:-1]
            assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", backend_docker_ip)
        self.address = (backend_docker_ip, self.backend_port)



    def __del__(self):
        if (self.docker_process):
            logging.info("Stopping backend ...\n")
            output=subprocess.check_output(['docker','rm','-f',self.docker_hash])
            self.docker_process.kill()

class Client(service_base.ServiceBase):
    def __init__(self):
        service_base.ServiceBase.__init__(self, [], None)
        self.docker_process = None


    def start_docker(self):
        #self.backend = BackendProxy()

        # get container IP
        # docker inspect --format = \'{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}\' d2cc496561d6
        backend_address = ("172.17.0.2", 45847)#self.backend.address
        child_id = self.repeater.connect_child_repeater(backend_address)
        self.child_services[child_id] = self.make_child_proxy(child_id, self)
        logging.info("Try ping")
        self.child_services[child_id].make_ping()


    def run(self):
        '''
        Process requests and answers.
        :return:
        '''

        # !! Timeout is internal timeout of the select method, loop runs infinitelly, must use some thread
        self.repeater.run(0.1) # run for some time
        logging.info("After run")
        while True:
            time.sleep(1)
            self.process_answers()



logging.basicConfig(filename='client_log', filemode="w", level=logging.DEBUG)

client = Client()
client.start_docker()
client.run()
