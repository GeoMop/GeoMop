import sys
import os
__ins_lib_dir__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "ins-lib")
sys.path.insert(1, __ins_lib_dir__)
import logging
import random
import os
import time

path = sys.argv[1]
number = random.randrange(0, 100000)
log_file = os.path.join(path, "MPI_" + str(number) + ".log")
logging.basicConfig(filename=log_file,level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')
logging.info("MPI Application " + str(number) + " is started")
logging.info("Task lib directory:" + __ins_lib_dir__ )
from mpi4py import MPI
size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

msg = "Hello world! I am process {0} of {1} on {2}.".format(str(rank), str(size), name)
logging.info(msg)

if __name__ != "job":
    for i in range(0, 30):
        time.sleep(30)
        logging.info( "time: " + str(i*30+30) + "s")
