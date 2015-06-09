import gettext

t = gettext.translation('editor', '../locale', fallback=True)

def gettext(text):
    return t.gettext(text)
