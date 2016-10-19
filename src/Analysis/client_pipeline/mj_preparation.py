import os
import shutil

from pipeline.parametrized_actions import *
from pipeline.generator_actions import *
from pipeline.wrapper_actions import *
from pipeline.data_types_tree import *
from pipeline.workflow_actions import *
from pipeline.pipeline import *
from pipeline.pipeline_processor import *
from pipeline.identical_list import *
import pipeline.action_types as action

from client_pipeline.parametrized_actions_preparation import *


class MjPreparation():
    @staticmethod
    def prepare(workspace, analysis, mj, python_script, pipeline_name):
        err = []

        # test if workspace dir exist
        if not os.path.isdir(workspace):
            err.append("Workspace directory don't exist.")
            return err

        # directory preparation
        mj_config_dir = os.path.join(workspace, analysis, mj, "mj", "mj_config")
        os.makedirs(mj_config_dir, exist_ok=True)

        # run script
        script_path = os.path.join(workspace, analysis, python_script)
        try:
            with open(script_path, 'r') as fd:
                script_text = fd.read()
        except (RuntimeError, IOError) as e:
            err.append("Can't open script file: {0}".format(e))
            return err
        exec(script_text)
        pipeline = locals()[pipeline_name]

        # validation
        pipeline._inicialize()
        e = pipeline.validate()
        if len(e) > 0:
            err.extend(e)
            return err

        # copy script
        shutil.copy(script_path, mj_config_dir)

        # prepare resources
        for res in pipeline.get_resources():
            if res["name"] == "Flow123d":
                Flow123dActionPreparation.prepare(res, mj_config_dir)
            else:
                err.append("Missing resource preparation for {0}.".format(res["name"]))

        # run script #2
        script_path = os.path.join(mj_config_dir, python_script)
        try:
            with open(script_path, 'r') as fd:
                script_text = fd.read()
        except (RuntimeError, IOError) as e:
            err.append("Can't open script file: {0}".format(e))
            return err
        exec (script_text)
        pipeline2 = locals()[pipeline_name]

        # validation #2
        pipeline2._inicialize()
        e = pipeline2.validate()
        if len(e) > 0:
            err.extend(e)
            return err

        return err
