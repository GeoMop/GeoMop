"""Icon manipulation library"""
import PyQt5.QtGui as QtGui
import PyQt5.QtCore as QtCore
import os

__icon_dir__ = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "icons")


# def set_path(file):
#     global __icon_dir__
#     __icon_dir__ = os.path.join(os.path.dirname(os.path.realpath(file)), "..", "gm_base", "resources",
#                                 "icons")


def get_file(name,  size):
    """Get file path to icon from archive"""
    name += ('_' + str(size))
    return os.path.join(__icon_dir__, name + ".png")


def get_icon(name,  size):
    """Get QIcon object from icon archive"""
    return QtGui.QIcon(get_file(name,  size))


def get_app_icon(name):
    """Get QIcon object from icon archive"""
    app_icon = QtGui.QIcon()
    availableSizes = [16, 24, 32, 48, 64, 128]
    try:
        for size in availableSizes:
            app_icon.addFile(get_file(name, size), QtCore.QSize(size, size))
        if len(app_icon.availableSizes()) == 0:
            raise NameError('LoadingError')
    except NameError:
        print(
            "Unable to load the icon '" + str(name) + "', missing program resources. "
            "Try checking directory: \n" + str(__icon_dir__)
        )
    # returns empty QIcon if loading fails and program run continues.
    return app_icon


def get_pixmap(name, size):
    """Get QPixmap object from icon archive"""
    return QtGui.QPixmap(get_file(name,  size))
