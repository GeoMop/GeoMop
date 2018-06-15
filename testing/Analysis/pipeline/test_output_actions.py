from Analysis.pipeline.output_actions import *
from Analysis.pipeline.generator_actions import *
from Analysis.pipeline.data_types_tree import *
from Analysis.pipeline.pipeline_processor import *
from Analysis.pipeline.pipeline import *


import shutil
import os


TEST_FILES = "test_files"


def test_print_dtt_action(request):
    def clear_test_files():
        shutil.rmtree("backup", ignore_errors=True)
        shutil.rmtree(TEST_FILES, ignore_errors=True)
    request.addfinalizer(clear_test_files)

    # create test files dir
    if not os.path.isdir(TEST_FILES):
        try:
            os.mkdir(TEST_FILES)
        except Exception as e:
            assert False

    # pipeline
    var = Ensemble(
        Struct(a=Float(), b=Int()),
        Struct(a=Float(1.0), b=Int(1)),
        Struct(a=Float(2.0), b=Int(2)),
        Struct(a=Float(3.0), b=Int(3)))
    gen = VariableGenerator(Variable=var)
    output_file = os.path.join(TEST_FILES, "output.txt")
    pa = PrintDTTAction(Inputs=[gen], OutputFile=output_file)
    pipeline = Pipeline(ResultActions=[pa])

    # pipeline processor
    pp = Pipelineprocessor(pipeline)

    # validation
    err = pp.validate()
    assert len(err) == 0

    # run pipeline
    pp.run()
    i = 0

    while pp.is_run():
        runner = pp.get_next_job()
        if runner is None:
            time.sleep(0.1)
        else:
            pp.set_job_finished(runner.id)
        i += 1
        assert i < 1000, "Timeout"

    # check result
    try:
        with open(output_file, 'r') as fd:
            assert fd.read() == "\n".join(var._get_settings_script()) + "\n"
    except (RuntimeError, IOError) as e:
        assert False
