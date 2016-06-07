#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start script that initializes main window and runs APP
@author: Jan Gabriel
@contact: jan.gabriel@tul.cz
"""
import os
import sys
import logging
import argparse
import PyQt5.QtWidgets as QtWidgets

# import common directory to path (should be in __init__)
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
sys.path.insert(1, __lib_dir__)
sys.path.insert(2, './twoparty/pexpect')
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(3, './twoparty/enum')

from ui.com_manager import ComManager
from ui.main_window import MainWindow
from ui.data.data_structures import DataContainer
import icon

# logging setup on STDOUT or to FILE
logger = logging.getLogger("UiTrace")

logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(
    '%(asctime)s|%(levelname)s: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)


class JobsScheduler(object):
    """Jobs Scheduler main class"""

    def __init__(self, args):
        """Initialization of UI with executive code"""
        # setup qt app
        self._app = QtWidgets.QApplication(args)
        
        #icon
        self._app.setWindowIcon(icon.get_app_icon("js-geomap"))

        # load data container
        self._data = DataContainer()

        # setup com manager
        self._com_manager = ComManager()

        # setup qt UI
        self._main_window = MainWindow(data=self._data,
                                       com_manager=self._com_manager)

        # connect reloader kill on app exit
        self._app.aboutToQuit.connect(
            self._main_window.handle_terminate)

        # connect save all on exit
        self._app.aboutToQuit.connect(self._data.save_all)

    @property
    def mainwindow(self):
        """Application main window."""
        return self._main_window

    def run(self):
        """Run app and show UI"""

        # show UI
        self._main_window.show()

        # execute app
        sys.exit(self._app.exec_())


def main():
    """JobsScheduler application entry point."""
    parser = argparse.ArgumentParser(description='JobsScheduler')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()

    if args.debug:
        from ui.data.data_structures import DataContainer
        DataContainer.DEBUG_MODE = True

    # logging
    if not args.debug:
        from geomop_util.logging import log_unhandled_exceptions

        def on_unhandled_exception(type_, exception, tback):
            """Unhandled exception callback."""
            # pylint: disable=unused-argument
            from geomop_dialogs import GMErrorDialog
            # display message box with the exception
            if jobs_scheduler is not None and jobs_scheduler.mainwindow is not None:
                err_dialog = GMErrorDialog(jobs_scheduler.mainwindow)
                err_dialog.open_error_dialog("Application performed invalid operation!",
                                             error=exception)
            sys.exit(1)

        log_unhandled_exceptions('JobsScheduler', on_unhandled_exception)

    # delete old lock files
    for root, dirs, files in os.walk("./lock", topdown=False):
        for name in files:
            if name != "source.lock":
                os.remove(os.path.join(root, name))
                logger.info("Old lock file was deleted: " + name)

    # init and run APP
    jobs_scheduler = JobsScheduler(sys.argv)
    jobs_scheduler.run()


if __name__ == "__main__":
    main()
