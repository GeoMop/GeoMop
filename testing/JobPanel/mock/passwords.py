import os


def get_passwords():
    """Return dict with passwords from secret file."""
    file = os.path.expanduser("~/.ssh/passwords")
    d = {}
    try:
        with open(file, 'r') as fd:
            for line in fd:
                line = line.split(sep="#", maxsplit=1)[0]
                line = line.strip()
                sp = line.split(sep=":")
                if len(sp) == 3:
                    d[sp[0]] = (sp[1], sp[2])
    except:
        pass
    return d


def get_test_password():
    u = "test"
    p = ""
    d = get_passwords()
    if "test" in d:
        u = d["test"][0]
        p = d["test"][1]
    return u, p
