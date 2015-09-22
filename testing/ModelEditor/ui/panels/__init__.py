"""
Inititliazes Qt application for component testing.
"""


def setup_module(module):
    """Setup any state specific to the execution of the given module."""
    from PyQt5.Qt import QApplication
    import sys
    module.app = QApplication(sys.argv)


def teardown_module(module):
    """Teardown any state that was previously setup with a setup_module method."""
    module.app.quit()
