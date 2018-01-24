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
import time

# import common directory to path (should be in __init__)
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "common")
__pexpect_dir__ = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "twoparty/pexpect")
__enum_dir__ = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "twoparty/enum")

sys.path.insert(1, __lib_dir__)
sys.path.insert(2, __pexpect_dir__)
if sys.version_info[0] != 3 or sys.version_info[1] < 4:
    sys.path.insert(3, __enum_dir__)

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "Analysis"))

#sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# needed if running from different directory

from ui.com_manager import ComManager
from ui.main_window import MainWindow
from ui.data.data_structures import DataContainer
from ui.imports.workspaces_conf import BASE_DIR
import icon
from  communication.installation import Installation

import config as cfg
CONFIG_DIR = os.path.join(cfg.__config_dir__, BASE_DIR)

from backend.service_frontend import ServiceFrontend

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


class JobPanel(object):
    """Jobs Panel main class"""

    def __init__(self, args):
        """Initialization of UI with executive code"""
        # setup qt app
        self._app = QtWidgets.QApplication(args)
        
        #icon
        self._app.setWindowIcon(icon.get_app_icon("js-geomap"))

        # load data container
        self._data = DataContainer()
        Installation.set_init_paths(CONFIG_DIR, self._data.workspaces.get_path())

        # setup com manager
        self._com_manager = ComManager(self._data)

        # setup frontend service
        self._frontend_service = ServiceFrontend(self._data)

        # setup qt UI
        self._main_window = MainWindow(data=self._data,
                                       com_manager=self._com_manager,
                                       frontend_service=self._frontend_service)

        # connect save all on exit
        self._app.aboutToQuit.connect(self._data.save_all)

    @property
    def mainwindow(self):
        """Application main window."""
        return self._main_window

    def run(self):
        """Run app and show UI"""

        # start frontend service
        self._frontend_service.run_before()

        # start backend service
        self._frontend_service.start_backend()

        # show UI
        self._main_window.show()

        # execute app
        ret = self._app.exec_()

        # stop backend service
        self._frontend_service.stop_backend()
        for i in range(10):
            time.sleep(0.1)
            self._frontend_service.run_body()

        # stop frontend service
        self._frontend_service.run_after()

        sys.exit(ret)


def main():
    """JobPanel application entry point."""
    parser = argparse.ArgumentParser(description='JobPanel')
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
            if job_panel is not None and job_panel.mainwindow is not None:
                err_dialog = GMErrorDialog(job_panel.mainwindow)
                err_dialog.open_error_dialog("Application performed invalid operation!",
                                             error=exception)
            sys.exit(1)

        log_unhandled_exceptions('JobPanel', on_unhandled_exception)

    # delete old lock files
    lock_dir = os.path.join(CONFIG_DIR , 'lock')
    
    for root, dirs, files in os.walk(lock_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
            logger.info("Old lock file was deleted: " + name)

    # init and run APP
    job_panel = JobPanel(sys.argv)
    job_panel.run()


if __name__ == "__main__":
    main()
