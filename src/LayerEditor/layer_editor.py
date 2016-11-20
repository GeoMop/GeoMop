"""Start script that inicialize main window """
import sys
import os
import signal
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)

import argparse
from ui import MainWindow
from leconfig import cfg
import PyQt5.QtWidgets as QtWidgets
import icon

class LayerEditor:
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
        for i in range(0, 50):
            for j in range(0, 50):
                x1 = i*50
                x2 = i*50+20*(i%9-5) +20*(j%11-6) 
                y1= j*50
                y2 = j*50 +30*(i%4) +20*(j%9-4) + j%7 
                p1 = diagram.add_point(x1, y1)
                diagram.add_line(p1, x2, y2)
        self.mainwindow.set_diagram_data(diagram)

    def main(self):
        """go"""        
        self._app.exec_()

def main():
    """LayerEditor application entry point."""
    parser = argparse.ArgumentParser(description='LayerEditor')
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
            if layer_editor is not None:
                err_dialog = None
                # display message box with the exception
                if layer_editor.mainwindow is not None:
                    err_dialog = GMErrorDialog(layer_editor.mainwindow)

                # try to reload editor to avoid inconsistent state
                if callable(layer_editor.mainwindow.reload):
                    try:
                        layer_editor.mainwindow.reload()
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
    layer_editor = LayerEditor()
    layer_editor.main()
    cfg.save()
    sys.exit(0)


if __name__ == "__main__":
    main()


