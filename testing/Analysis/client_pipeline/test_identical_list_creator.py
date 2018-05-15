from Analysis.client_pipeline.identical_list_creator import *
import os
import shutil


TEST_FILES = "test_files"


def test_compare_list(request):
    def clear_test_files():
        shutil.rmtree(TEST_FILES, ignore_errors=True)
    request.addfinalizer(clear_test_files)

    # create test files dir
    if not os.path.isdir(TEST_FILES):
        try:
            os.mkdir(TEST_FILES)
        except Exception as e:
            assert False

    # save
    cl = {"1": "hash_1", "2": "hash_2", "3": "hash_3"}
    file = os.path.join(TEST_FILES, "compare_list.json")
    err = ILCreator.save_compare_list(cl, file)
    assert len(err) == 0

    # load
    err, cl2 = ILCreator.load_compare_list(file)
    assert len(err) == 0

    # compare
    assert cl == cl2


def test_create_identical_list():
    cl_old = {"1": "hash_1", "2": "hash_2", "3": "hash_3"}
    cl_new = {"4": "hash_1", "5": "hash_2", "6": "hash_7"}
    il = ILCreator.create_identical_list(cl_new, cl_old)
    assert il._instance_dict == {"4": "1", "5": "2"}
