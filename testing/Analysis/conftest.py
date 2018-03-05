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

def check_unique_import(pkg):
    for path in sys.path:
        pkg_path = os.path.join(path, pkg)
        #print(pkg_path)
        if os.path.isdir(pkg_path):
            print("pkg path: ", pkg_path)


check_unique_import("pipeline")

#import pipeline
#import client_pipeline.identical_list_creator