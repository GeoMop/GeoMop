"""
Script to remove *.pyc files from specified directories.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

import os
import fnmatch
import sys
import logging

logger = logging.getLogger("Remote")


def remove_pyc(*args):
    """Remove *.pyc from directory and all subdirectories."""
    for root_dir in args:
        if not os.path.isdir(root_dir):
            logger.warn("remove_pyc: {} is not a directory, skipping".format(root_dir))
            continue

        logger.debug("Removing *.pyc files in {}".format(root_dir))
        for root, __, files in os.walk(root_dir):
            for file in fnmatch.filter(files, "*.pyc"):
                path = os.path.join(root, file)
                os.remove(path)


if __name__ == '__main__':
    remove_pyc(*sys.argv[1:])
