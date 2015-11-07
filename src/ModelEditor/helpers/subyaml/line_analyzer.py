"""Line Analyzer provides functions to analyze a single line of text.

.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""
import re


_re_strip_eol = re.compile(r'[^\n]*')
_re_begins_with_comment = re.compile(r'(\s*)#')
_re_uncomment = re.compile(r'(\s*)# ?(.*)')


def strip_to_line(function):
    """Decorator to strip the first argument of a function to a single line without EOL.

    :param function: the function to be wrapped
    """

    def wrapped(*args, **kwargs):
        args = list(args)
        text = args[0]
        line = _re_strip_eol.match(text).group(0)
        args[0] = line
        return function(*args, **kwargs)

    return wrapped


class LineAnalyzer:
    """Anayze partial yaml line

    Description: This quick party text analyzing contains line
    specific function.
    """

    @staticmethod
    def get_char_poss(line, tag):
        """Return possition of tag ended by space or new line"""
        index = line.find(tag + " ")
        if index == -1:
            index = line.find(tag)
            if index > -1 and len(line) != (index+1):
                return -1
        return index
        
    @classmethod
    def get_separator(cls,  line, char,  start, end):
        """Return possition of char between start and end or -1"""
        line = cls.strip_comment(line)
        index = line.find(char, start, end)
        return index
        
    @staticmethod
    def get_changed_position(new_line, old_line):
        """
        Return start, end possition of changed text
        
        Start possition is from beginning and
        last possition is from end        
        """
        end_pos = 1
        before_pos = 0
        if len(old_line) != 0 and len(new_line) != 0:
            while new_line[before_pos] == old_line[before_pos]:
                before_pos += 1
                if (len(new_line) == before_pos or
                        len(old_line) == before_pos):
                    break
            while new_line[-end_pos] == old_line[-end_pos]:
                end_pos += 1
                if (len(new_line) <= end_pos or
                        len(old_line) <= end_pos):
                    break
        return before_pos, end_pos 
    
    @classmethod
    def get_key_area(cls, line):
        """
        get key area for one line

        return if is, end_of_area (-1 end of line)
        """
        key = re.match(r'[^:]+:\s*$', line)
        if key is not None:
            return True, -1
        key = re.match(r'([^:]+:\s)', line)
        if key is not None:
            dist = key.end(1)
            res, dist2 = cls.get_after_key_area(line[dist:])
            if not res:
                return True, dist
            if dist2 == -1:
                return True, -1
            return True, dist + dist2
        return False, 0

    @classmethod
    def get_after_key_area(cls, line):
        """
        Test if line begin with special areas (tag, ref, anchor)

        return if is, end_of_arrea (-1 end of line)
        """
        line = cls.strip_comment(line)
        area = re.match(r'\s*$', line)
        if area is not None:
            # empty line
            return True, -1
        for char in ['!', '&', '<<: \*', '\*']:
            index = line.find(char)
            if index > -1:
                area = re.match(r'\s*(' + char + r'\S+\s*)$', line)
                if area is not None:
                    # area is all line
                    return True, -1
                area = re.match(r'\s*(' + char + r'\S+\s+)\S', line)
                if area is not None:
                    dist = area.end(1)
                    res, dist2 = cls.get_after_key_area(line[dist:])
                    if not res:
                        return True, dist
                    if dist2 == -1:
                        return True, -1
                    return True, dist + dist2
        return False, 0

    @staticmethod
    def strip_comment(line):
        """return line witout comments"""
        # TODO write tests and refactor "key: abc ## comment"
        comment = re.search(r'^(.*\S)\s*#.*$', line)
        if comment:
            return comment.group(1)
        else:
            return line

    @staticmethod
    def indent_changed(new_row, old_row):
        """compare intendation two rows"""
        if old_row.isspace() or len(old_row) == 0:
            return False
        old_value = re.search(r'^\s*\S', old_row)
        new_value = re.search(r'^\s*\S', new_row)
        if not old_value and not new_value:
            return False
        if not old_value or not new_value:
            return True
        return not len(old_value.group(0)) == len(new_value.group(0))
        
    @staticmethod
    def get_indent(row):
        """return intendation of row"""
        if row.isspace():
            return len(row)
        value = re.search(r'^(\s*)-\s', row)
        if not value :
            value = re.search(r'^(\s+)\S', row)
        if not value :
            return 0
        return len(value.group(1))
     
    @staticmethod
    def is_array_char_only(row):
        """return if is on line only arry char"""
        value = re.search(r'^\s*-\s*$', row)
        if not value :
            return False
        return True

    @staticmethod
    @strip_to_line
    def begins_with_comment(line):
        """Check if line begins with a comment.

        The line can contain any number of whitespace characters before the first
        comment sign :samp:`#`.

        :param str line: a line of text
        :return: True if line begins with a comment, False otherwise
        :rtype: bool
        """
        return _re_begins_with_comment.match(line) is not None

    @staticmethod
    @strip_to_line
    def uncomment(line):
        """Remove comment symbol at the start of the line and leave indentation level intact.

        If the comment symbol :samp:`#` is immediately followed by a space, remove it as well.

        :param str line: a line of text possibly starting with a comment symbol
        :return: line without the leading comment symbol
        :rtype: str
        """
        match = _re_uncomment.match(line)
        if not match:
            return line
        else:
            return match.group(1) + match.group(2)
