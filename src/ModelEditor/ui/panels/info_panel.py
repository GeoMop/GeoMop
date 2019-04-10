"""
Info Panel Widget

Widget that shows info text with QWebEngineView.

.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from urllib.parse import urlparse, parse_qs
import os
from copy import copy

from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtCore import QUrl, Qt
import PyQt5.QtCore as QtCore

from ModelEditor.ist import InfoTextGenerator
from ModelEditor.util import CursorType
from ModelEditor.meconfig import MEConfig as cfg

# pylint: disable=invalid-name

class InfoPanelPage(QWebEnginePage):
    def __init__(self, parent = None):
        super().__init__(parent)

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

        # self.setMinimumSize(700, 200)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        #self.setFocusPolicy(Qt.NoFocus)

        self._html_root_url = QUrl.fromLocalFile(cfg.info_text_html_root_dir + os.path.sep)


    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """
        Overloaded method for own processing of navigation events.
        Return True if the url should be loaded.
        """
        if (navigation_type == QWebEnginePage.NavigationTypeLinkClicked):
            self.navigate_to(url)
        return True

    def update_from_node(self, node, cursor_type=None):
        """Update the info text for the given node and cursor_type.

        :param DataNode node: current node
        :param CursorType cursor_type: indicates cursor position in node
        """
        is_parent = self._is_parent(cursor_type, node)
        node, data = node.get_info_text_data(is_parent)

        parent = {}
        parent['id'] = None
        parent['arr'] = []
        while node.parent is not None:
            node, next_parent = node.get_info_text_data(False)
            parent['arr'].append(next_parent)
        self.update_from_data(data, True, parent)

    def _is_parent(self, cursor_type, node):
        """return if parent is need for info"""
        is_parent = False
        if node.parent is not None and node.parent.implementation == node.Implementation.sequence:
            is_parent = True
        elif cursor_type == CursorType.value.value:
            new_node = node.get_node_at_position(node.span.start)
            if new_node is not None:
                node = new_node
        elif cursor_type == CursorType.parent.value:
            is_parent = True
        return is_parent

    def update_from_data(self, data, set_home, parent=None):
        """Generate and show the info text from data.

        :param dict data: query data; generally IDs or values necessary to generate InfoText
        :param bool set_home: when True, this info_text is set as default and browsing history is
           reset
        """
        self._data = data
        if set_home:
            if parent is None:
                parent = {}
                parent['id'] = None
                parent['arr'] = []
            self._context['home'] = self._data
            self._context['back'] = []
            self._context['forward'] = []
            self._context['parent'] = parent
            self._context['parent_id'] = 0
        args = copy(self._data)
        args.update({'context': self._context})
        html = InfoTextGenerator.get_info_text(**args)
        self.setHtml(html, self._html_root_url)

    def navigate_to(self, url_):
        """Navigate to given URL.

        :param QUrl url_: the url containing the query data to navigate to
        """
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
            self._context['parent']['id'] = None
            del data['home']
        elif 'parent' in data:
            self._context['back'].append(self._data)
            del data['parent']
        else:
            self._context['back'].append(self._data)
            self._context['forward'].clear()

        self.update_from_data(data, set_home=False)




def main():
    """Launches the widget for testing/debugging purposes."""
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QTimer

    app = QApplication(sys.argv)
    url = QUrl.fromLocalFile(os.path.join(cfg.info_text_html_root_dir, 'katex_example.html'))
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

if __name__ == '__main__':
    main()
