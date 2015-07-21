import data.yaml
import yaml
import data.data_node as dn
import difflib


class DocumentParser:
    """
    Parses the document.

    Uses the last valid version of the file to eliminate a single
    parsing error (within an edited block).

    If there are multiple or unresolvable errors (i.e. deleted end of flow
    style), it marks the rest of the document invalid (parse error).
    """

    def __init__(self):
        self.parsed_doc = ""
        """last parsed YAML document - without a parsing error"""
        self.current_doc = ""
        """current document to parse"""
        self._loader = data.yaml.Loader()
        self._errors = []
        self._error_line = None
        self._error_end_pos = None

    @property
    def errors(self):
        """Tuple of parsing errors."""
        # TODO: transform _errors into DataError
        raise NotImplementedError

    def parse(self, current_doc):
        """
        Parses the current document and fills the error array with
        parsing errors.
        """
        self._errors = []
        self.current_doc = current_doc
        try:
            root_node = self._loader.load(self.current_doc)
        except yaml.MarkedYAMLError as yaml_error:
            self._error_line = self._get_error_line_from_yaml_error(yaml_error)
            doc_lines = self._remove_diff_block_at_position()
            self._report_parsing_error(yaml_error)
            try:
                document = ''.join(doc_lines)
                root_node = self._loader.load(document)
            except yaml.MarkedYAMLError as yaml_error:  # multiple or unresolvable errors
                self._error_end_pos = self._get_eof_position()
                self._error_line = self._get_error_line_from_yaml_error(yaml_error)
                self._report_parsing_error(yaml_error)
                self.parsed_doc = ''.join(doc_lines[0:self._error_line])
                root_node = self._loader.load(self.parsed_doc)
            else:  # one parsing error, remainder ok
                self.parsed_doc = document
        else:
            self.parsed_doc = self.current_doc
        return root_node

    def _remove_diff_block_at_error_line(self):
        """Removes the diff block of code at error position."""
        parsed_doc_lines = self.parsed_doc.splitlines(keepends=True)
        current_doc_lines = self.current_doc.splitlines(keepends=True)
        sm = difflib.SequenceMatcher(current_doc_lines, parsed_doc_lines)
        for tag, cur_start_line, cur_end_line, par_start_line, par_end_line \
                in sm.get_opcodes():
            pass
        # SequenceMatcher diff
        # replace all until error
        # comment out entire block at position
        # replace all
        # TODO: set self._error_end_position = end of diff area
        # return document with some lines commented out
        pass

    def _get_error_line_from_yaml_error(self, yaml_error):
        if yaml_error.problem_mark is not None:
            line = yaml_error.problem_mark.line
        else:
            line = yaml_error.context_mark.line
        return line

    def _report_parsing_error(self, yaml_error):
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.error
        description = yaml_error.problem
        start_pos = dn.Position(self._error_line + 1, 1)
        span = dn.Span(start=start_pos, end=self._error_end_pos)
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def _get_eof_position(self):
        # TODO: replace with static? util lib
        eof_line = len(self.current_doc) - 1
        eof_column = len(self.current_doc[eof_line]) - 1
        return dn.Position(eof_line + 1, eof_column + 1)
