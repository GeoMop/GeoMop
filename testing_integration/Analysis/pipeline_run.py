import os
import shutil
import subprocess

from client_pipeline.mj_preparation import *
from pipeline.pipeline_processor import *

# setting testing directory
test_dir = "d:/test/pipeline_run"


# remove old files
workspace = os.path.join(test_dir, "workspace")
shutil.rmtree(workspace, ignore_errors=True)

# copy files to testing directory
shutil.copytree("pipeline_run_res/workspace", workspace)

# prepare mj
analysis="an1"
mj="mj1"
python_script="s.py"
pipeline_name="Pipeline_5"
err = MjPreparation.prepare(workspace=workspace, analysis=analysis, mj=mj,
                            python_script=python_script, pipeline_name=pipeline_name)
if len(err) > 0:
    for e in err:
        print(e)
    exit()

# mj_config_dir
mj_config_dir = os.path.join(workspace, analysis, "mj", mj, "mj_config")

# change cwd
cwd = os.getcwd()
os.chdir(mj_config_dir)

# run script
try:
    with open(python_script, 'r') as fd:
        script_text = fd.read()
except (RuntimeError, IOError) as e:
    print("Can't open script file: {0}".format(e))
    exit()
exec(script_text)
pipeline = locals()[pipeline_name]

# pipeline processor
pp = Pipelineprocessor(pipeline)

# validation
err = pp.validate()
if len(err) > 0:
    for e in err:
        print(e)
    exit()

# run pipeline
names = []
pp.run()
i = 0

while pp.is_run():
    runner = pp.get_next_job()
    if runner is None:
        time.sleep(0.1)
    else:
        names.append(runner.name)
        command = runner.command
        if command[0] == "flow123d":
            command[0] = "flow123d.bat"
        process = subprocess.Popen(command, stderr=subprocess.PIPE)
        return_code = process.wait(10)
        if return_code is not None:
            #print(process.stderr)
            pass
        pp.set_job_finished(runner.id)
    i += 1
    assert i < 1000, "Timeout"

print("\nrun flows\n---------")
for name in names:
    print(name)
print("")

# return cwd
os.chdir(cwd)
