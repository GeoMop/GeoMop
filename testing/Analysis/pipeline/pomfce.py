import os


def compare_with_file(fname, lines):
    """
    :param fname: reference file path
    :param lines: actual output
    :return:
    """
    with open(fname) as f:
        res = f.readlines()
        i=0
        for line in res:
            if i==len(lines):
                assert False, \
                    "Line {0} is not in result\n{1}".format(str(i+1),line.rstrip())
                break
            assert line.rstrip() == lines[i].rstrip(), \
                "on line {0}\n{1}\n<>\n{2}".format(str(i+1),line.rstrip() ,lines[i].rstrip())
            i += 1
        assert i>=len(res), \
            "Line {0} is not in file\n{1}".format(str(i+1),lines[i].rstrip())    


def remove_if_exist(file):
    if os.path.isfile(file):
        os.remove(file)
