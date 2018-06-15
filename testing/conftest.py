"""
Common test configuration for all test subdirectories.
Put here only those things that can not be done through command line options and pytest.ini file.
"""


import sys
import os
import shutil
import pytest
import PyQt5.Qt as Qt


print("Root conf test.")
# Modify sys.path to have path to the GeoMop modules.
# TODO: make installation and Tox working in order to remove this hack.
this_source_dir = os.path.dirname(os.path.realpath(__file__))
rel_paths = ["../src", "../submodules/intersections/src"]
for rel_path in rel_paths:
    sys.path.append(os.path.realpath(os.path.join(this_source_dir, rel_path)))
sys.path = [ x for x in sys.path if x not in {this_source_dir, ''} ]
print(sys.path)


# def test_exit_button(qtbot, monkeypatch):
#     exit_calls = []
#     monkeypatch.setattr(QApplication, 'exit', lambda: exit_calls.append(1))
#     button = get_app_exit_button()
#     qtbot.click(button)
#     assert exit_calls == [1]
#

# Since 'request' and 'monkeypatch' have different scope they can not be used together
# in qapp fixture. This workaround use monkeypatch directly without fixture syntax.
#from _pytest.monkeypatch import MonkeyPatch

# A fixture that starts and teardown QApplication correctly.
# Use for tests that do not test code that starts QAplication itself, these
# must delete QApplication instance itself.

# TODO:
# Modify application classes to not calling QApplication but taking it as parameter,
# Use pytest-qt for QT tests using single QApplication object and monkeypatching qapp.exit,
# auxiliary exit should call closeAllWindows and QApplication should set no call of exit when main window.
# QBot fixture manage closing registered widgets and starting next test.

@pytest.fixture
def qapp(request):
    """Qt application fixture"""
    print("Creating test QApplication")

    app = Qt.QApplication(sys.argv)
    print("Fixture app: ", str(app))

    # # Can not use 'yield' approach for teardown since
    # # it isn't called if the test throws.
    # def qapp_teardown():
    #     print("Delete fixture app: ", str(app))
    #     del app
    # request.addfinalizer(qapp_teardown)
    # yield app

    yield app
    print("Delete fixture app: ", str(app))
    app.closeAllWindows()
    del app

@pytest.fixture
def paths_to_remove():
    """
    Fixture for removing paths (files and dirs) after test ends.
    Usage:
    def test_a(paths_to_remove):
        file = "file.txt"
        paths_to_remove.append(file)
        write_file(file)
        check_file(file)
    """
    paths_to_remove = []
    yield paths_to_remove
    for path in paths_to_remove:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

@pytest.fixture
def change_dir_back():
    """
    After test ends change working directory to original directory which was before test start.
    Usage:
    def test_a(change_dir_back):
        os.chdir("work_dir")
        some_work()
    """
    class ChangeDirBack:
        def __init__(self):
            self._old_dir = os.getcwd()

        def _change_back(self):
            os.chdir(self._old_dir)

    change_dir_back = ChangeDirBack()
    yield
    change_dir_back._change_back()
