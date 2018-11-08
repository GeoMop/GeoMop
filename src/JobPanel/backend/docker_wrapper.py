"""
Docker wrapper
The only possible way to get std output from docker execution.
"""

import os
import sys
import subprocess


GEOMOP_INTERNAL_DIR_NAME = ".geomop"
"""We do not import from gm_base.config due to potential import error."""

args = sys.argv[1:]
if not args:
    sys.exit(1)

os.makedirs(GEOMOP_INTERNAL_DIR_NAME, exist_ok=True)
out_file = os.path.join(GEOMOP_INTERNAL_DIR_NAME, "docker_std_out.txt")
with open(out_file, 'w') as fd_out:
    process = subprocess.Popen(args, stdout=fd_out, stderr=subprocess.STDOUT)
process.wait()
