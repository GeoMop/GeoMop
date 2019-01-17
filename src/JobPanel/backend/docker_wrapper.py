"""
Docker wrapper
The only possible way to get std output from docker execution.
"""

import os
import sys
import subprocess

from gm_base.global_const import GEOMOP_INTERNAL_DIR_NAME


args = sys.argv[1:]
if not args:
    sys.exit(1)

os.makedirs(GEOMOP_INTERNAL_DIR_NAME, exist_ok=True)
out_file = os.path.join(GEOMOP_INTERNAL_DIR_NAME, "docker_std_out.txt")
with open(out_file, 'w') as fd_out:
    try:
        process = subprocess.Popen(args, stdout=fd_out, stderr=subprocess.STDOUT)
    except OSError as e:
        fd_out.write("Error in starting docker process:\n{}: {}\n".format(e.__class__.__name__, e))
    else:
        process.wait()
