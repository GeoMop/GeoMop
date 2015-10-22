"""
Info Panel Widget

This module contains a widget that shows info text with QWebView.
"""

from urllib.parse import urlparse, parse_qs
import os

from PyQt5.QtWebKitWidgets import QWebView, QWebPage
from PyQt5.QtCore import QUrl

from ist import InfoTextGenerator
from data import CursorType
from copy import copy

# pylint: disable=invalid-name

__author__ = 'Tomas Krizek'

__html_root_path__ = os.path.join(os.getcwd(), 'resources', 'ist_html') + os.path.sep


class InfoPanelWidget(QWebView):
    """Widget for displaying HTML info text."""

    def __init__(self, parent=None):
        """Initializes the class."""
        super(InfoPanelWidget, self).__init__(parent)

        self._context = {
            'home': None,
            'back': [],
            'forward': []
        }
        """
        Dictionary with keys `home`, `back`, `forward`. Home contains query data for the
        automatically selected node. Back and forward are lists of query data.
        """

        self._data = None
        """ Query data of currently displayed page."""

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

    def update_from_data(self, data, set_home=True):
        """Generates and shows the info text from data."""
        self._data = data
        if set_home:
            self._context['home'] = self._data
            self._context['back'] = []
            self._context['forward'] = []
        args = copy(self._data)
        args.update({'context': self._context})
        html = InfoTextGenerator.get_info_text(**args)
        super(InfoPanelWidget, self).setHtml(html, self._html_root_url)

    def navigate_to(self, url_):
        """Navigates to given URL."""
        query_params = parse_qs(urlparse(url_.toString()).query)
        data = {name: value[0] for name, value in query_params.items()}

        if 'forward' in data and len(self._context['forward']) > 0:
            self._context['forward'].pop()
            self._context['back'].append(self._data)
            del data['forward']
        elif 'back' in data and len(self._context['back']) > 0:
            self._context['back'].pop()
            self._context['forward'].append(self._data)
            del data['back']
        elif 'home' in data:
            self._context['back'].clear()
            self._context['forward'].clear()
            del data['home']
        else:
            self._context['back'].append(self._data)
            self._context['forward'].clear()

        self.update_from_data(data, set_home=False)

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
