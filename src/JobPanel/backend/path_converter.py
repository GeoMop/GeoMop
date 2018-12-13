import re
import sys


def win2lin_conv_path(path):
    """Converts win path to linux path."""
    if re.match("^[a-zA-Z]:", path):
        path = "/" + path[0].lower() + path[2:]
    path = path.replace("\\", "/")
    return path


def if_win_win2lin_conv_path(path):
    """If platform is win converts win path to linux path."""
    if sys.platform == "win32":
        return win2lin_conv_path(path)
    else:
        return path


def lin2win_conv_path(path):
    """Converts lin path to win path."""
    if re.match("^/[a-z]", path):
        path = path[1].upper() + ":" + path[2:]
    path = path.replace("/", "\\")
    return path


def if_win_lin2win_conv_path(path):
    """If platform is win converts linux path to win path."""
    if sys.platform == "win32":
        return lin2win_conv_path(path)
    else:
        return path
