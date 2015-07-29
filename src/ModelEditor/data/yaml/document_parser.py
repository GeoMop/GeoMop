import data.yaml
import yaml
import data.data_node as dn
import difflib
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
        self.parsed_doc = ""
        """last parsed YAML document - without a parsing error"""
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
            doc_lines = self._remove_diff_blocks()
            self.error_handler.report_parsing_error(yaml_error, self._error_end_pos)
            try:
                document = ''.join(doc_lines)
                root_node = self._loader.load(document)
            except yaml.MarkedYAMLError as yaml_error:  # multiple or unresolvable errors
                self.error_handler.report_parsing_error(yaml_error, self._get_eof_position())
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
                    self.error_handler.report_modification_ignored(
                        cur_start_line, cur_end_line)
            if self._error_end_pos is None:
                self._error_end_pos = dn.Position(cur_end_line + 1, 1)
        return current_doc_lines

    def _get_eof_position(self):
        eof_line = len(self.current_doc) - 1
        eof_column = len(self.current_doc[eof_line]) - 1
        return dn.Position(eof_line + 1, eof_column + 1)
