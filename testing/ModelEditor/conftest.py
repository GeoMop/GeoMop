"""Tests configuration.

Contains scope-wide fixtures.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
print("conftest ModelEditor")



import sys
import os
import pytest

# Modify sys.path for all tests in testing/ModelEditor
this_source_dir = os.path.dirname(os.path.realpath(__file__))
rel_paths = ["../../src"]
for rel_path in rel_paths:
    sys.path.append(os.path.realpath(os.path.join(this_source_dir, rel_path)))

#for path in sys.path:
#    ui_path = os.path.join(path, "ui")
#    print(ui_path)
#    if os.path.isdir(ui_path):
#        print("UI path: ", ui_path)
#print(sys.path)


from PyQt5.Qt import QApplication

from ModelEditor.ui.panels.yaml_editor import YamlEditorWidget


@pytest.fixture(scope='session')
def qapp(request):
    """Qt application"""
    app = QApplication(sys.argv)
    def fin():
        app.quit()
    request.addfinalizer(fin)
    return app


@pytest.fixture(scope='session')
def editor(qapp):
    return YamlEditorWidget()
