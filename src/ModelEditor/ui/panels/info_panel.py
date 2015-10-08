"""
Info Panel Widget

This module contains a widget that shows info text with QWebView.
"""

# pylint: disable=invalid-name

__author__ = 'Tomas Krizek'

from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtCore import QUrl
import os

__html_root_path__ = os.path.join(os.getcwd(), 'resources', 'ist_html') + os.path.sep


class InfoPanelWidget(QWebView):
    """Widget for displaying HTML info text."""

    def __init__(self, parent=None):
        """Initializes the class."""
        super(InfoPanelWidget, self).__init__(parent)
        self.setMinimumSize(800, 250)
        self._html_root_url = QUrl.fromLocalFile(__html_root_path__)
        self.linkClicked.connect(self.navigate_to)
        self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)

    def update_from_node(self, node, cursor_type=None):
        """Updates the info text for the given node and cursor_type."""
        self.setHtml(node.get_info_text(cursor_type))

    def setHtml(self, html):
        """Sets the HTML content of info panel."""
        from ist import InfoTextGenerator
        html = InfoTextGenerator.get_info_text("7f7b2caffb3e4eb6", "time_step")
        super(InfoPanelWidget, self).setHtml(html, self._html_root_url)
        print('\n\n' + html)

    def navigate_to(self, url_):
        """Navigates to given URL."""
        # TODO: is support for links needed?
        print('navigate-to: ' + url_.toString())

    def resizeEvent(self, event):
        """Handle window resize."""
        super(InfoPanelWidget, self).resizeEvent(event)
        self.page().setViewportSize(event.size())


if __name__ == '__main__':
    def main():
        """Launches the widget."""
        import sys
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer

        app = QApplication(sys.argv)
        url = QUrl.fromLocalFile(__html_root_path__ + 'katex_example.html')
        win = InfoPanelWidget()
        win.setUrl(url)
        win.show()

        def refresh_page():
            """Page refresh for debugging purposes."""
            win.setUrl(url)

        timer = QTimer(win)
        timer.timeout.connect(refresh_page)
        timer.start(5000)

        sys.exit(app.exec_())

    main()
