"""Icon manimulation library"""
import PyQt5.QtGui as QtGui
import os

__icon_dir__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icon")

def get_file(name,  size):
    """Get file object"""
    path = __icon_dir__
    if size == 24:
        path = os.path.join(path, "24x24")
    elif size == 16:
        path = os.path.join(path, "16x16")
    return os.path.join(path,name + ".png")

def get_icon(name,  size):
    """Get QIcon object"""
    return QtGui.QIcon(get_file(name,  size))
    
def get_pixmap(name,  size):
    """Get QIcon object"""
    return QtGui.QPixmap(get_file(name,  size))
