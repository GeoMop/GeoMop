from Analysis.client_pipeline.mj_preparation import *
from Analysis.client_pipeline.parametrized_actions_preparation import Flow123dActionPreparation
from Analysis.pipeline.pipeline_processor import *
from gm_base.geomop_analysis import YamlSupportLocal

import time
import subprocess
import os


def load_pipeline(python_script="analysis.py", pipeline_name="pipeline"):
    """Loads pipeline from script and return it."""
    err = []
    try:
        with open(python_script, 'r') as fd:
            script_text = fd.read()
    except (RuntimeError, IOError) as e:
        err.append("Can't open script file: {0}".format(e))
        return err, None
    action_types.__action_counter__ = 0
    loc = {}
    try:
        exec(script_text, globals(), loc)
    except Exception as e:
        err.append("Error in analysis script: {0}: {1}".format(e.__class__.__name__, e))
        return err, None
    if pipeline_name not in loc:
        err.append('Analysis script must create variable named "{}".'.format(pipeline_name))
        return err, None
    pipeline = loc[pipeline_name]
    return err, pipeline


def check_pipeline(pipeline):
    """Check pipeline and return list of errors"""
    err = []

    e = _create_support_files(pipeline)
    if len(e) > 0:
        err.extend(e)
        return err

    # pipeline processor
    pp = Pipelineprocessor(pipeline)

    # validation
    e = pp.validate()
    if len(e) > 0:
        err.extend(e)
        return err

    return err


def export_pipeline(pipeline, dir_path, python_script="analysis.py", pipeline_name="pipeline"):
    """Exports pipeline to define directory."""
    err = []

    # make export dir
    os.makedirs(dir_path, exist_ok=True)

    # save script
    pipeline._inicialize()
    script = '\n'.join(pipeline._get_settings_script()) + '\n'
    script = script.replace(pipeline._get_instance_name(), pipeline_name)
    try:
        with open(os.path.join(dir_path, python_script), 'w') as fd:
            fd.write(script)
    except Exception as e:
        err.append("Script saving error: {0}".format(e))
        return err

    # prepare resources
    for res in pipeline.get_resources():
        if res["name"] == "Flow123d":
            e, input_files = Flow123dActionPreparation.prepare(res, os.getcwd(), dir_path)
            if len(e) > 0:
                err.extend(e)
                return err
        else:
            err.append("Missing resource preparation for {0}.".format(res["name"]))

    return err


def run_pipeline(pipeline, executables):
    """Runs pipeline"""
    err = []

    e = _create_support_files(pipeline)
    if len(e) > 0:
        err.extend(e)
        return err

    # pipeline processor
    pp = Pipelineprocessor(pipeline)

    # validation
    e = pp.validate()
    if len(e) > 0:
        err.extend(e)
        return err

    # run pipeline
    pp.run()
    while pp.is_run():
        runner = pp.get_next_job()
        if runner is None:
            time.sleep(0.1)
        else:
            command = runner.command
            if command[0] in executables:
                command = command.copy()
                command[0] = executables[command[0]]
            process = subprocess.Popen(command, cwd=runner.work_dir)
            process.wait()
            pp.set_job_finished(runner.id)

    return err


def _create_support_files(pipeline):
    err = []
    for res in pipeline.get_resources():
        if res["name"] == "Flow123d":
            yaml_file = res["YAMLFile"]
            ys = YamlSupportLocal()
            e = ys.parse(yaml_file)
            if len(e) > 0:
                err.extend(e)
                return err
            dir, name = os.path.split(yaml_file)
            s = name.rsplit(sep=".", maxsplit=1)
            new_name = s[0] + ".sprt"
            sprt_file = os.path.join(dir, new_name)
            ys.save(sprt_file)
    return err
