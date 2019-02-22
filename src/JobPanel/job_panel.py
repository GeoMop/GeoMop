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

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

#from JobPanel.ui.com_manager import ComManager
from JobPanel.ui.main_window import MainWindow
from JobPanel.ui.dialogs.docker_machine_start_dialog import DockerMachineStartDialog
from JobPanel.ui.data.data_structures import DataContainer
from JobPanel.ui.imports.workspaces_conf import BASE_DIR
import gm_base.icon as icon
from JobPanel.communication.installation import Installation

import gm_base.config as cfg
CONFIG_DIR = os.path.join(cfg.__config_dir__, BASE_DIR)

from JobPanel.backend.service_frontend import ServiceFrontend

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
        self._app.setWindowIcon(icon.get_app_icon("geomap"))

        # load data container
        self._data = DataContainer()
        Installation.set_init_paths(CONFIG_DIR, self._data.workspaces.get_path())

        # setup com manager
        #self._com_manager = ComManager(self._data)

        # todo: presunuto z main_window, nevim jeslti to je v poradku
        # select workspace if none is selected
        if self._data.workspaces.get_path() is None:
            import sys
            sel_dir = QtWidgets.QFileDialog.getExistingDirectory(None, "Choose workspace")
            if not sel_dir:
                sys.exit(0)
            elif sys.platform == "win32":
                sel_dir = sel_dir.replace('/', '\\')
            self._data.reload_workspace(sel_dir)

        # setup frontend service
        self._frontend_service = ServiceFrontend(self._data)

        # setup qt UI
        self._main_window = MainWindow(data=self._data,
                                       frontend_service=self._frontend_service)

        # connect save all on exit
        self._app.aboutToQuit.connect(self._data.save_all)

    @property
    def mainwindow(self):
        """Application main window."""
        return self._main_window

    def run(self):
        """Run app and show UI"""

        # on win start Docker Machine
        if sys.platform == "win32":
            dlg = DockerMachineStartDialog()
            if not dlg.exec():
                sys.exit(1)

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
        self._frontend_service.kill_backend()

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
        from gm_base.geomop_util.logging import log_unhandled_exceptions

        def on_unhandled_exception(type_, exception, tback):
            """Unhandled exception callback."""
            # pylint: disable=unused-argument
            from gm_base.geomop_dialogs import GMErrorDialog
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
