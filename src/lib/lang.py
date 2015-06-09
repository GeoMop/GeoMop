import gettext

t = gettext.translation('lib', '../locale', fallback=True)

def gettext(text):
    return t.gettext(text)
