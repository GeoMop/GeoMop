"""Start script that inicialize main window """
import sys
import os
import signal
#__lib_dir__ = os.path.join(os.path.split(
#    os.path.dirname(os.path.realpath(__file__)))[0], "gm_base")
#sys.path.insert(1, __lib_dir__)

import argparse
from .ui import MainWindow
from .aeconfig import cfg
import PyQt5.QtWidgets as QtWidgets
import gm_base.icon as icon

class AnalyzisEditor:
    """Analyzis editor main class"""
    
    def __init__(self):
        # load config
        cfg.init()
        
        # main window
        self._app = QtWidgets.QApplication(sys.argv)
        self._app.setWindowIcon(icon.get_app_icon("me-geomap"))
        self.mainwindow = MainWindow(self)

        # show
        self.mainwindow.show()
        
        #test
        import ui.data as data
        diagram = data.Diagram()
        n1 = diagram.add_node(100, 200, 0)
        n2 = diagram.add_node(100, 400, 0)
        diagram.add_connection(n1, n2)
        self.mainwindow.set_diagram_data(diagram)

    def main(self):
        """go"""        
        self._app.exec_()

def main():
    """AnalyzisEditor application entry point."""
    parser = argparse.ArgumentParser(description='AnalyzisEditor')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    if args.debug:
        cfg.config.__class__.DEBUG_MODE = True

    # logging
    if not args.debug:
        from geomop_util.logging import log_unhandled_exceptions

        def on_unhandled_exception(type_, exception, tback):
            """Unhandled exception callback."""
            # pylint: disable=unused-argument
            from geomop_dialogs import GMErrorDialog
            if analyzis_editor is not None:
                err_dialog = None
                # display message box with the exception
                if analyzis_editor.mainwindow is not None:
                    err_dialog = GMErrorDialog(analyzis_editor.mainwindow)

                # try to reload editor to avoid inconsistent state
                if callable(analyzis_editor.mainwindow.reload):
                    try:
                        analyzis_editor.mainwindow.reload()
                    except:
                        if err_dialog is not None:
                            err_dialog.open_error_dialog("Application performed invalid operation!",
                                                         error=exception)
                            sys.exit(1)

                if err_dialog is not None:
                    err_dialog.open_error_dialog("Unhandled Exception!", error=exception)

        log_unhandled_exceptions(cfg.config.__class__.CONTEXT_NAME, on_unhandled_exception)

    # enable Ctrl+C from console to kill the application
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # launch the application
    analyzis_editor = AnalyzisEditor()
    analyzis_editor.main()
    cfg.save()
    sys.exit(0)


if __name__ == "__main__":
    main()


