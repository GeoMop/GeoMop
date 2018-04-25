"""Icon manipulation library"""
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import os

__icon_dir__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "icons")

def get_file(name,  size):
    """Get file path to icon from archiv"""
    path = __icon_dir__
    if size == 16:
        name += '_16'
    elif size == 24:
        name += '_24'
    elif size == 32:
        name += '_32'
    elif size == 48:
        name += '_48'
    elif size == 64:
        name += '_64'
    elif size == 128:
        name += '_128'
    return os.path.join(path,name + ".png")

def get_icon(name,  size):
    """Get QIcon object from icon archiv"""
    return QtGui.QIcon(get_file(name,  size))
    
def get_app_icon(name):
    """Get QIcon object from icon archiv"""
    app_icon = QtGui.QIcon()
    app_icon.addFile(get_file(name,  16), QtCore.QSize(16,16))
    app_icon.addFile(get_file(name,  24), QtCore.QSize(24,24))
    app_icon.addFile(get_file(name,  32), QtCore.QSize(32,32))
    app_icon.addFile(get_file(name,  48), QtCore.QSize(48,48))    
    app_icon.addFile(get_file(name,  64), QtCore.QSize(64,64))
    app_icon.addFile(get_file(name,  128), QtCore.QSize(128,128))
    return app_icon
    
def get_pixmap(name,  size):
    """Get QPixmap object from icon archiv"""
    return QtGui.QPixmap(get_file(name,  size))
