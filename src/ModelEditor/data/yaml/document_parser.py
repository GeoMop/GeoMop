import data.yaml
import yaml
import data.data_node as dn
import data.error_handler as eh


class DocumentParser:
    """
    Parses the document.

    Uses the last valid version of the file to eliminate a single
    parsing error (within an edited block).

    If there are multiple or unresolvable errors (i.e. deleted end of flow
    style), it marks the rest of the document invalid (parse error).
    """

    def __init__(self, error_handler):
        """initialize the class with ErrorHandler"""
        self.current_doc = ""
        """current document to parse"""
        self.error_handler = error_handler
        self._loader = data.yaml.Loader(error_handler)
        self._error_end_pos = None
        self._error_line = None

    def parse(self, current_doc):
        """
        Parses the current document and fills the error array with
        parsing errors.
        """
        self.current_doc = current_doc
        try:
            root_node = self._loader.load(self.current_doc)
        except yaml.MarkedYAMLError as yaml_error:
            self._error_line = eh.get_error_line_from_yaml_error(yaml_error)
            self.current_doc = self._comment_until_eof()
            self.error_handler.clear()
            self.error_handler.report_parsing_error(yaml_error, self._error_end_pos)
            try:
                root_node = self._loader.load(self.current_doc)
            except yaml.MarkedYAMLError:  # unresolvable error
                root_node = None
        return root_node

    def _comment_until_eof(self):
        """Comments out document until end of file from error line."""
        current_doc_lines = self.current_doc.splitlines(keepends=True)
        self._error_end_pos = self._get_eof_position()
        i = self._error_line
        while i < len(current_doc_lines):
            current_doc_lines[i] = '#' + current_doc_lines[i]
            i += 1
        return ''.join(current_doc_lines)

    def _get_eof_position(self):
        eof_line = len(self.current_doc) - 1
        eof_column = len(self.current_doc[eof_line]) - 1
        return dn.Position(eof_line + 1, eof_column + 1)
