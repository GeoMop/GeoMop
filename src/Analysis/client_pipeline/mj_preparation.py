import os
import shutil

from pipeline import *

from client_pipeline.parametrized_actions_preparation import *
from client_pipeline.identical_list_creator import *

class MjPreparation():
    @staticmethod
    def prepare(workspace, analysis, mj, python_script, pipeline_name, last_analysis=None):
        err = []

        # workspace absolute path
        workspace = os.path.realpath(workspace)

        # test if workspace dir exist
        if not os.path.isdir(workspace):
            err.append("Workspace directory don't exist.")
            return err

        # directory preparation
        analysis_dir = os.path.join(workspace, analysis)
        mj_dir = os.path.join(analysis_dir, "mj", mj)
        mj_config_dir = os.path.join(mj_dir, "mj_config")
        os.makedirs(mj_config_dir, exist_ok=True)
        mj_precondition_dir = os.path.join(mj_dir, "mj_precondition")
        os.makedirs(mj_precondition_dir, exist_ok=True)

        # change cwd
        cwd = os.getcwd()
        os.chdir(analysis_dir)

        # run script
        #script_path = os.path.join(workspace, analysis, python_script)
        try:
            with open(python_script, 'r') as fd:
                script_text = fd.read()
        except (RuntimeError, IOError) as e:
            err.append("Can't open script file: {0}".format(e))
            return err
        exec(script_text)
        pipeline = locals()[pipeline_name]

        # pipeline inicialize
        pipeline._inicialize()

        # copy script
        shutil.copy(python_script, mj_config_dir)

        # prepare resources
        for res in pipeline.get_resources():
            if res["name"] == "Flow123d":
                e = Flow123dActionPreparation.prepare(res, analysis_dir, mj_config_dir)
                if len(e) > 0:
                    err.extend(e)
                    return err
            else:
                err.append("Missing resource preparation for {0}.".format(res["name"]))

        # change cwd
        os.chdir(mj_config_dir)

        # run script #2
        try:
            with open(python_script, 'r') as fd:
                script_text = fd.read()
        except (RuntimeError, IOError) as e:
            err.append("Can't open script file: {0}".format(e))
            os.chdir(cwd)
            return err
        exec(script_text)
        pipeline2 = locals()[pipeline_name]

        # validation #2
        pipeline2._inicialize()
        e = pipeline2.validate()
        if len(e) > 0:
            err.extend(e)
            os.chdir(cwd)
            return err

        # return cwd
        os.chdir(cwd)

        # create compare list
        compare_list = pipeline2._get_hashes_list()
        e = ILCreator.save_compare_list(compare_list, os.path.join(mj_precondition_dir, "compare_list.json"))
        if len(e) > 0:
            err.extend(e)
            return err

        # create identical list
        if last_analysis is not None:
            last_cl_file = os.path.join(workspace, last_analysis, "mj", mj, "mj_precondition", "compare_list.json")
            if os.path.isfile(last_cl_file):
                e, last_cl = ILCreator.load_compare_list(last_cl_file)
                if len(e) > 0:
                    err.extend(e)
                    return err
                il = ILCreator.create_identical_list(compare_list, last_cl)
                il.save(os.path.join(mj_config_dir, "identical_list.json"))

        # copy backup files
        if last_analysis is not None:
            shutil.copytree(os.path.join(workspace, last_analysis, "mj", mj, "mj_config", "backup"),
                            os.path.join(mj_config_dir, "backup"))

        return err
