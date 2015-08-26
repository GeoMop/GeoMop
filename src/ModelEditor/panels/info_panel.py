from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtCore import QUrl


class InfoPanelWidget(QWebView):

    def __init__(self, parent=None):
        super(InfoPanelWidget, self).__init__(parent)
        self.setUrl(QUrl('http://localhost:8000/index.html'))
        # self.webView.setUrl(QUrl.fromLocalFile('/home/sharp/projects/Flow123d-python-utils/docs/index.html'))
#         self.setHtml('''<html><head><link href="css/test.css" media="screen" rel="stylesheet" type="text/css"></head><body>
#  <h1>HTML Previewer</h1>
#  <a href="https://seznam.cz">Linkaroo</a>
#   <p>This example shows you how to use QtWebKitWidgets.QWebView to
#    preview HTML data written in a QtWidgets.QPlainTextEdit.
#   </p>
# </body></html>''')
        self.linkClicked.connect(self.navigateTo)

    def setHtml(self, html):
        """Sets the HTML content of info panel."""
        # TODO: change link location?
        super(InfoPanelWidget, self).setHtml(html, QUrl.fromLocalFile(('/home/sharp/projects/GeoMop/src/lib/ist/')))
        # temp = self.settings().testAttribute(self.settings().JavascriptEnabled)
        print("\n\n" + html + "\n\n")
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

    def navigateTo(self, url):
        """Navigates to given URL."""
        print('navigate-to: ' + url.toString())


if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    win = InfoPanelWidget()
    win.show()

    sys.exit(app.exec_())
