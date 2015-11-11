Linux Installation Guide
========================

.. highlight:: bash

The following guide describes the installation of GeoMop on a debian-based operating system.
This guide was tested on Debian 8 (kernel 3.16.0-4-amd64).

System pre-requisites
---------------------

- git
- Python 3
- PyQt5 with QScintilla and QWebKit
- pip3

You can obtain all of these with the following command::

  $ sudo apt-get install git python3 python3-pip python3-pyqt5 python3-pyqt5.qsci python3-pyqt5.qtwebkit


Virtual Environment
-------------------

This step is optional. However, it is recommended to use virtual environments
to avoid issues with conflicting dependencies of various Python projects. If you
create a separate virtual environment for each Python project, the projects might
use different versions of the same library without any issues. Using a virtual
environment also ensures that you will not interfere with packages or libraries
required by your operating system.

First, install the virtualenvwrapper using pip3 and create your virtualenvs folder::

  $ sudo pip3 install virtualenvwrapper
  $ mkdir ~/.virtualenvs

Append these commands to your shell startup file (``~/.bashrc``)::

  export WORKON_HOME=~/.virtualenvs
  export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
  source /usr/local/bin/virtualenvwrapper.sh

After you open a *new terminal instance*, you should be able to run the following command
to crate a new virtual environment::

  $ mkvirtualenv GeoMop
  ...
  (GeoMop) $

The ``(GeoMop) $`` label indicates that you're currently working in a GeoMop virtual environment.
You should make sure to work in this environment every time you want to run the GeoMop application
or install its dependencies using pip etc. Once you have created the virtual environment, you
can activate it using the ``workon`` command::

  $ workon GeoMop

When you wish to quit the virtual environment, you can use the ``deactivate`` command::

  (GeoMop) $ deactivate
  $

Linking PyQt5
  If you're using virtual environment, it is necessary to link the PyQt5 library and its
  dependencies to your virtual environment, otherwise the Python interpreter won't be able to
  locate them::

    ln -s /usr/lib/python3/dist-packages/PyQt5 ~/.virtualenvs/GeoMop/lib/python3.4/PyQt5
    ln -s /usr/lib/python3/dist-packages/sip.cpython-34m-x86_64-linux-gnu.so ~/.virtualenvs/GeoMop/lib/python3.4/sip.so

  If the commands are not able to locate the files, your distribution's path to PyQt5 and sip may
  be different. Please locate the correct path and link the packages to the virtual environment.

Note
  When you're using virtual environment, you should not require root privileges to manage
  pip packages or run any commands in the virtual environment. Unless you created the
  environment as a root - in that case, you should consider changing the ownership of
  the ``.virtualenvs`` folder to a regular user account.

  If you use the ``sudo`` command, it will invoke the system pip3 instead of the virtual
  environment pip3. This might lead to accidentally installation, update or removal of
  system-wide python packages instead of the virtual environments packages.

Cloning the project repository
------------------------------

The development version of GeoMop can be found at `github <https://github.com/GeoMop/GeoMop>`_::

  $ git clone https://github.com/GeoMop/GeoMop.git

The latest release version is currently located in the `release` branch::

  $ cd GeoMop
  $ git checkout release

Python package dependencies
---------------------------

To install all the required Python packages, make sure you're in the root folder of the git repository.

If you're using virtual environment, don't forget to activate it::

  $ workon GeoMop
  (GeoMop) $ pip3 install -r requirements.txt

If you're **NOT** using virtual environment, run the command with root privileges::

  $ sudo pip3 install -r requirements.txt

Launching the application
-------------------------

Running the **Model Editor**::

  (GeoMop) $ python3 src/ModelEditor/model_editor.py
