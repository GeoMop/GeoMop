"""Tests configuration.

Contains scope-wide fixtures.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
print("conftest ModelEditor")


import sys
import pytest



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
