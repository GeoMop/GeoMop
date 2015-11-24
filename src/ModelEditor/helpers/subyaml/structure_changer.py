"""Structure changer.


.. codeauthor:: Pavel Richter <pavel.richter@tul.cz>
"""
import re

class StructureChanger:
    """
    Function for formating and adding yaml text
    """
    __indent__ = 2
    """File default indentation"""
    __line_length__ = 60
    """File default indentation"""
    
    
    def __init__(self):
        """init"""
        pass

    @staticmethod
    def copy_structure(lines, l1, c1, l2, c2, indent):
        """
        Copy structure from lines to separate array. Structure is
        move by indentation. 
        """
        add = []
        # try add comments
        if l1 == l2:
            add.append(indent*" " + lines[l1][c1:c2])
        else:
            from_line = l1
            if c1 > 0:
                add.append(indent*" " + lines[l1][c1:])
                from_line += 1
            indentation2 = re.search(r'^(\s*)(\S.*)$', lines[l1])
            indentation2 = len(indentation2.group(1))
            indentation = indent - indentation2
            for i in range(from_line, l2):
                indentation_test = re.search(r'^(\s*)(\S.*)$', lines[i])
                if indentation == 0 or len(indentation_test.group(1)) < -indentation:
                    add.append(lines[i])
                elif indentation < 0:
                    add.append(lines[i][-indentation:])
                else:
                    add.append(indentation*" " + lines[i])
            indentation_test = re.search(r'^(\s*)(\S.*)$', lines[l2])
            if len(indentation_test.group(1)) <= c2:
                if indentation == 0 or len(indentation_test.group(1)) < -indentation:
                    add.append(lines[l2][:c2])
                elif indentation < 0:
                    add.append(lines[l2][-indentation:c2])
                else:
                    add.append(indentation*" " + lines[l2][:c2])
        return add
        
    @staticmethod
    def skip_key(self, lines, l1, c1, l2, c2):
        """return new value possition witout tag, anchor or ref"""
        for char in ["!", r'\*', r'<<:\s*\*', "&"]:
            nl1 = l1
            nc1 = c1
            if lines[nl1][nc1:].isspace() or len(lines[nl1]) <= nc1:
                nl1 += 1
                nc1 = 0
                if nl1 > l2:
                    return l1, c1
                while lines[nl1].isspace() or len(lines[nl1]) == 0:
                    nl1 += 1
                    if nl1 > l2:
                        return l1, c1
            tag = re.search(r'^(\s*' + char + r'\S*)', lines[nl1][nc1:])
            if tag is not None:
                nc1 += len(tag.group(1))
                if len(lines[nl1]) >= nc1:
                    nl1 += 1
                    nc1 = 0
                    if nl1 > l2:
                        return l1, c1
                c1 = nc1
                l1 = nl1
        return l1, c1
