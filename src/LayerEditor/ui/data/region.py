from PyQt5 import QtGui


class Region:
    _cols = ["cyan", "magenta", "darkRed", "darkCyan", "darkMagenta",
             "darkBlue", "yellow","blue"]
    # red and green is used for cut tool resp. cloud pixmap
    colors = [ QtGui.QColor(col) for col in _cols]
    id_next = 1



    def __init__(self, id = None, color = None, name="", dim=0):
        if id is None:
            id = Region.id_next
            Region.id_next += 1
        self.id = id

        if color is None:
            color = Region.colors[self.id%len(Region.colors)].name()
        self.color = color

        self.name = name
        """Region name"""
        self.dim = dim
        """dimension (point = 0, well = 1, fracture = 2, bulk = 3)"""

# Special instances
Region.none = Region(0, "grey", "NONE", -1)