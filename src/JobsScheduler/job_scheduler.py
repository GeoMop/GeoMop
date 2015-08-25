"""Start script that initializes main window """

import os
import sys
__lib_dir__ = os.path.join(os.path.split(
    os.path.dirname(os.path.realpath(__file__)))[0], "lib")
sys.path.insert(1, __lib_dir__)

import os
import PyQt5.QtCore as QtCore
import PyQt5.QtWidgets as QtWidgets


class JobsScheduler:
    """Jobs Scheduler main class"""

    def __init__(self):
        """Initialization of UI"""
        
        # main_window
        self._app = QtWidgets.QApplication(sys.argv)
        self._v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self._main_window = QtWidgets.QMainWindow()
        self._main_window.setCentralWidget(self._v_splitter)


        # menu_bar
        menu_bar = self._main_window.menuBar()

        # menu
        self._menu = menu_bar.addMenu('&Menu')
        # exit_action
        self._menu_exit_action = QtWidgets.QAction('&Exit', self._main_window)
        self._menu_exit_action.setShortcut('Ctrl+Q')
        self._menu_exit_action.setStatusTip('Exit application')
        self._menu_exit_action.triggered.connect(QtWidgets.qApp.quit)
        self._menu.addAction(self._menu_exit_action)

        # multijob
        self._multijob = menu_bar.addMenu('&MultiJob')
        # add_action
        self._multijob_add_action = QtWidgets.QAction('&Add',
                                                      self._main_window)
        self._multijob_add_action.setShortcut('Alt+A')
        self._multijob_add_action.setStatusTip('Add new MultiJob')
        self._multijob_add_action.triggered.connect(self._add_multijob)
        self._multijob.addAction(self._multijob_add_action)

        # copy_or_edit_action
        self._multijob_copy_edit_action = QtWidgets.QAction('&Copy | Edit',
                                                            self._main_window)
        self._multijob_copy_edit_action.setShortcut('Alt+C')
        self._multijob_copy_edit_action.setStatusTip('Copy or Edit MultiJob')
        self._multijob_copy_edit_action.triggered.connect(
            self._copy_edit_multijob)
        self._multijob.addAction(self._multijob_copy_edit_action)

        # run_or_stop_action
        self._multijob_run_stop_action = QtWidgets.QAction('&Run | Stop',
                                                           self._main_window)
        self._multijob_run_stop_action.setShortcut('Alt+R')
        self._multijob_run_stop_action.setStatusTip('Run or Stop selected '
                                                    'MultiJob')
        self._multijob_run_stop_action.triggered.connect(
            self._run_stop_multijob)
        self._multijob.addAction(self._multijob_run_stop_action)

        # delete_action
        self._multijob_delete_action = QtWidgets.QAction('&Delete',
                                                         self._main_window)
        self._multijob_delete_action.setShortcut('Alt+D')
        self._multijob_delete_action.setStatusTip('Delete selected MultiJob')
        self._multijob_delete_action.triggered.connect(
            self._delete_multijob)
        self._multijob.addAction(self._multijob_delete_action)

        # settings
        self._settings = menu_bar.addMenu('&Settings')
        # resource_action
        self._settings_resource_action = QtWidgets.QAction('&Resource',
                                                           self._main_window)
        self._settings_resource_action.setShortcut('Shift+R')
        self._settings_resource_action.setStatusTip('Show resources')
        self._settings_resource_action.triggered.connect(
            self._resource_settings)
        self._settings.addAction(self._settings_resource_action)

        # ssh_action
        self._settings_ssh_action = QtWidgets.QAction('&SSH Connections',
                                                           self._main_window)
        self._settings_ssh_action.setShortcut('Shift+S')
        self._settings_ssh_action.setStatusTip('Show ssh connections')
        self._settings_ssh_action.triggered.connect(
            self._ssh_settings)
        self._settings.addAction(self._settings_ssh_action)

        # pbss_action
        self._settings_pbss_action = QtWidgets.QAction('&PBSs',
                                                           self._main_window)
        self._settings_pbss_action.setShortcut('Shift+P')
        self._settings_pbss_action.setStatusTip('Show available PBSs')
        self._settings_pbss_action.triggered.connect(
            self._pbss_settings)
        self._settings.addAction(self._settings_pbss_action)

        self._table = QtWidgets.QTableView(self._v_splitter)
        self._v_splitter.addWidget(self._table)

        self._tab = QtWidgets.QTabWidget(self._v_splitter)
        self._v_splitter.addWidget(self._tab)


        # main window show
        self._main_window.show()

    # menu action
    def _exit_menu(self):
        pass

    #multijob actions
    def _add_multijob(self):
        pass

    def _copy_edit_multijob(self):
        pass

    def _run_stop_multijob(self):
        pass

    def _delete_multijob(self):
        pass

    #settings actions
    def _resource_settings(self):
        pass

    def _ssh_settings(self):
        pass

    def _pbss_settings(self):
        pass

    def main(self):
        """Main entry point"""
        self._app.exec_()

if __name__ == "__main__":
    JobsScheduler().main()
