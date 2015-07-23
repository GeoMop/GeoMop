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
        return list(self._errors)

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
            doc_lines = self._remove_diff_blocks()
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

    def _remove_diff_blocks(self):
        """Removes the diff block of code at error position."""
        # pylint: disable=invalid-name,unused-variable
        parsed_doc_lines = self.parsed_doc.splitlines(keepends=True)
        current_doc_lines = self.current_doc.splitlines(keepends=True)
        if not self.parsed_doc:  # no previous version, invalidate until the end
            self._error_end_pos = self._get_eof_position()
            i = self._error_line
            while i < len(current_doc_lines):
                current_doc_lines[i] = '#' + current_doc_lines[i]
                i += 1

        else:  # parsed_doc is not empty - find modifications
            self._error_end_pos = None
            sm = difflib.SequenceMatcher(a=current_doc_lines, b=parsed_doc_lines)
            cur_end_line = 0
            for tag, cur_start_line, cur_end_line, __, __ \
                    in sm.get_opcodes():
                # comment out edited lines
                if tag == 'replace' or tag == 'delete':
                    i = cur_start_line
                    while i < cur_end_line:
                        current_doc_lines[i] = '#' + current_doc_lines[i]
                        i += 1
                    if self._error_end_pos is None and self._error_line < cur_end_line:
                        # set end mark for parser error
                        self._error_end_pos = dn.Position(cur_end_line + 1, 1)
                    # show user info on commented out blocks
                    self._report_modification_ignored(cur_start_line, cur_end_line)
            if self._error_end_pos is None:
                self._error_end_pos = dn.Position(cur_end_line + 1, 1)
        return current_doc_lines

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

    def _report_modification_ignored(self, start_line, end_line):
        category = dn.DataError.Category.yaml
        severity = dn.DataError.Severity.info
        description = "Modifications ignored. Please fix parsing error(s) first."
        start_pos = dn.Position(start_line + 1, 1)
        end_pos = dn.Position(end_line + 1, 1)
        span = dn.Span(start=start_pos, end=end_pos)
        error = dn.DataError(category, severity, description, span)
        self._errors.append(error)

    def _get_eof_position(self):
        eof_line = len(self.current_doc) - 1
        eof_column = len(self.current_doc[eof_line]) - 1
        return dn.Position(eof_line + 1, eof_column + 1)
