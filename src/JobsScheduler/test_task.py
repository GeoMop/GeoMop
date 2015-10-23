import sys
sys.path.insert(1, './ins-lib')

import logging
import random
from mpi4py import MPI
import os

path = sys.argv[1]

number = random.randrange(0, 100000)
log_file = os.path.join(path, "MPI_" + str(number) + ".log")
logging.basicConfig(filename=log_file,level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')
logging.info("MPI Application " + str(number) + " is started")

size = MPI.COMM_WORLD.Get_size()
rank = MPI.COMM_WORLD.Get_rank()
name = MPI.Get_processor_name()

msg = "Hello world! I am process {0} of {1} on {2}.".format(str(rank), str(size), name)
logging.info(msg)     
