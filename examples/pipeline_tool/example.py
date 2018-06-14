import os
import sys

geomop_root = "/home/radek/work/GeoMop/src"
executables = {"flow123d": "/home/radek/work/Flow123d-2.1.0-linux-install/bin/flow123d.sh"}

#sys.path.append(os.path.join(geomop_root, "Analysis"))
#sys.path.append(os.path.join(geomop_root, "gm_base"))

import Analysis.pipeline_tool as pipeline_tool


def print_errors(err):
    if len(err) > 0:
        for e in err:
            print(e)
        sys.exit()


# loads pipeline from "analysis.py"
err, pipeline = pipeline_tool.load_pipeline()
print_errors(err)

# checks pipeline
err = pipeline_tool.check_pipeline(pipeline)
print_errors(err)

# run pipeline
err = pipeline_tool.run_pipeline(pipeline, executables)
print_errors(err)

# exports pipeline to "export_dir" directory
#err = pipeline_tool.export_pipeline(pipeline, "export_dir")
#print_errors(err)
