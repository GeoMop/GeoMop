# TODO: Install sources as packages and remove hacking sys.path
# Configuration file for pytest for Analysis directory.
import os
import sys

# Remove previous modification.
while "src" in sys.path[-1]:
    sys.path.pop(-1)

this_source_dir = os.path.dirname(os.path.realpath(__file__))
rel_paths = ["../../src", "../../src/common"]
for rel_path in rel_paths:
    sys.path.append(os.path.realpath(os.path.join(this_source_dir, rel_path)))

def check_unique_import(pkg):
    for path in sys.path:
        pkg_path = os.path.join(path, pkg)
        #print(pkg_path)
        if os.path.isdir(pkg_path):
            print("pkg path: ", pkg_path)


check_unique_import("data")

# import pkgutil
#
# import data
#
# package = data
# print("pkg path: ", package.__path__)
# for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
#     print("Found submodule %s (is a package: %s)" % (modname, ispkg))