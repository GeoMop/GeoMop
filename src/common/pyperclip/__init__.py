"""
Pyperclip

A cross-platform clipboard module for Python. (only handles plain text for now)
By Al Sweigart al@inventwithpython.com
BSD License

Usage:
  import pyperclip
  pyperclip.copy('The text to be copied to the clipboard.')
  spam = pyperclip.paste()

  if not pyperclip.copy:
    print("Copy functionality unavailable!")

On Windows, no additional modules are needed.
On Mac, this module makes use of the pbcopy and pbpaste commands, which should come with the os.
On Linux, this module makes use of the xclip or xsel commands, which should come with the os. Otherwise run "sudo apt-get install xclip" or "sudo apt-get install xsel"
  Otherwise on Linux, you will need the gtk or PyQt4 modules installed.

The gtk module is not available for Python 3, and this module does not work with PyGObject yet.
"""
__version__ = '1.5.24'

import platform
import os
import subprocess
from .clipboards import (init_xclip_clipboard, init_no_clipboard)
from .windows import init_windows_clipboard

PY2 = '2' == platform.python_version_tuple()[0]
STRING_FUNCTION = unicode if PY2 else str

# `import PyQt4` sys.exit()s if DISPLAY is not in the environment.
# Thus, we need to detect the presence of $DISPLAY manually not not load PyQt4 if it is absent.
HAS_DISPLAY = "DISPLAY" in os.environ or not (os.name == 'posix' or platform.system() == 'Linux')
CHECK_CMD = "where" if platform.system() == "Windows" else "which"


def _executable_exists(name):
    return subprocess.call([CHECK_CMD, name],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def determine_clipboard():
    # Determine the OS/platform and set the copy() and paste() functions accordingly.
    if 'cygwin' in platform.system().lower():
        return init_windows_clipboard(cygwin=True)
    if os.name == 'nt' or platform.system() == 'Windows':
        return init_windows_clipboard()
    if HAS_DISPLAY:
        if _executable_exists("xclip"):
            return init_xclip_clipboard()

    return init_no_clipboard()


def set_clipboard(clipboard):
    global copy, paste

    if clipboard == 'xclip':
        copy, paste = init_xclip_clipboard()
    elif clipboard == 'no':
        copy, paste = init_no_clipboard()
    elif clipboard == 'windows':
        copy, paste = init_windows_clipboard()


copy, paste = determine_clipboard()

__all__ = ["copy", "paste"]
