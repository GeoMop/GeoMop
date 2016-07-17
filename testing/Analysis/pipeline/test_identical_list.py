from pipeline.identical_list import *
import os
import shutil


TEST_FILES = "test_files"


def test_identical_list(request):
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
    il = IdenticalList({"1": "2", "3": "4", "5": "6"})
    file = os.path.join(TEST_FILES, "compare_list.json")
    il.save(file)

    # load
    il2 = IdenticalList()
    assert il2.load(file)

    # compare
    assert il._instance_dict == il2._instance_dict
