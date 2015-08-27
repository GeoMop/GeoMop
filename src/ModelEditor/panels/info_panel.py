# from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtCore import QUrl
import os

__html_root_path__ = os.path.join(
    os.path.split(os.path.dirname(os.path.realpath(__file__)))[0],
    "..", 'lib', 'ist', 'html_root') + os.path.sep


class InfoPanelWidget(QWebView):
    """Widget for displaying HTML info text."""

    def __init__(self, parent=None):
        """Initializes the class."""
        super(InfoPanelWidget, self).__init__(parent)
        self._html_root_url = QUrl.fromLocalFile(__html_root_path__)
        self.linkClicked.connect(self.navigateTo)
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

    def setHtml(self, html):
        """Sets the HTML content of info panel."""
        # TODO: change link location?
        super(InfoPanelWidget, self).setHtml(html, self._html_root_url)

    def navigateTo(self, url):
        """Navigates to given URL."""
        # TODO: is support for links needed?
        print('navigate-to: ' + url.toString())


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer

    app = QApplication(sys.argv)
    url = QUrl.fromLocalFile(__html_root_path__ + 'katex_example.html')
    win = InfoPanelWidget()
    win.setUrl(url)
    win.show()

    # for debugging purposes
    # def refreshPage():
    #     win.setUrl(url)
    #
    # timer = QTimer(win)
    # timer.timeout.connect(refreshPage)
    # timer.start(5000)

    sys.exit(app.exec_())
