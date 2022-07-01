#!/bin/python

# Update version.yml
# Usage:
# python update_version.py [version] [flow_version]
#
# Set content to:
# build: <to actual shorten git hash>
# date: <actual tiem and date>
# version: <optionaly set to new given version>
# flow_version: <optionaly set to new given version>

from ruamel.yaml import YAML
import ruamel.yaml
import os
import sys
from subprocess import check_output
from datetime import datetime


this_source_dir = os.path.dirname(os.path.realpath(__file__))
version_yaml = os.path.join(this_source_dir, "..", "version.yml")

yaml = YAML(typ="safe")
with open(version_yaml, 'r') as f:    
    content = ruamel.yaml.round_trip_load(f)

if len(sys.argv) > 1:
    version = argv[1]
else:
    version = content['version']

if len(sys.argv) > 2:
    flow_version = argv[2]
else:
    flow_version = content['flow123d_version']
    
git_hash = check_output(['git', 'rev-parse', '--short', 'HEAD']).decode("utf-8").strip()
git_branch = check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode("utf-8").strip()
build = f"{git_branch}_{git_hash}"


# datetime object containing current date and time
now = datetime.now()
date_time = now.strftime("%Y.%m.%d %H:%M:%S")
result = dict(
    version=version,
    flow123d_version=flow_version,
    build=build,
    date=date_time
    )
#print(result)    

with open(version_yaml+"_", 'w') as f:
    ruamel.yaml.round_trip_dump(result, f)

    

print(version)
