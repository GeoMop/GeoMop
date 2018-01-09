"""Keyboard shortcuts definition.
"""


DEFAULT_USER_SHORTCUTS = {
    # editor actions
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Y',

    # menu actions
    'new_file': 'Ctrl+N',
    'open_file': 'Ctrl+O',
    'save_file': 'Ctrl+S',
    'save_file_as': 'Ctrl+Shift+S',
    'exit': 'Ctrl+Q',
    'display': 'Ctrl+Shift+D',
    'display_all': 'Ctrl+Shift+L',
    'display_area': 'Ctrl+Shift+R',
}
"""default keyboard shortcuts"""


SHORTCUT_LABELS = {
    # editor actions
    'undo': 'Undo an action',
    'redo': 'Redo an action',
    # menu actions
    'new_file': 'New file',
    'open_file': 'Open file',
    'save_file': 'Save file',
    'save_file_as': 'Save file as',
    'exit': 'Quit application',
    'display': 'Display set area',
    'display_all': 'Display all shapes',
    'display_area': 'Display area',
}
"""labels of shortcuts to be displayed in the user interface"""


SYSTEM_SHORTCUTS = {
    # editor actions
    'copy': 'Ctrl+C',
    'paste': 'Ctrl+V',
    'cut': 'Ctrl+X',
    'select_all': 'Ctrl+A',
    'deselect_all': 'Ctrl+Shift+A',
    'delete': 'Delete',
}
"""system keyboard shortcuts that can not be changed by user"""
