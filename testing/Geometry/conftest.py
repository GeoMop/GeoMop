# TODO: Install sources as packages and remove hacking sys.path
# Configuration file for pytest for Analysis directory.
import os
import sys

# Remove previous modification.
while "src" in sys.path[-1]:
    sys.path.pop(-1)

# Modify sys.path for all tests in testing/ModelEditor
this_source_dir = os.path.dirname(os.path.realpath(__file__))
rel_paths = ["../../src"]
for rel_path in rel_paths:
    sys.path.append(os.path.realpath(os.path.join(this_source_dir, rel_path)))

