"""
Info Panel Widget

This module contains a widget that shows info text with QWebView.
"""

from urllib.parse import urlparse, parse_qs
import os

from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtCore import QUrl

from ist import InfoTextGenerator
from data import CursorType, ScalarNode

# pylint: disable=invalid-name

__author__ = 'Tomas Krizek'

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
        is_parent = False
        if cursor_type == CursorType.value.value:
            node = node.get_node_at_position(node.span.start)
        elif cursor_type == CursorType.parent.value:
            is_parent = True
        data = node.get_info_text_data(is_parent)
        self.update_from_data(data)

    def update_from_data(self, data):
        """Generates and shows the info text from data."""
        html = InfoTextGenerator.get_info_text(**data)
        super(InfoPanelWidget, self).setHtml(html, self._html_root_url)

    def navigate_to(self, url_):
        """Navigates to given URL."""
        query_params = parse_qs(urlparse(url_.toString()).query)
        data = {name: value[0] for name, value in query_params.items()}
        self.update_from_data(data)

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
