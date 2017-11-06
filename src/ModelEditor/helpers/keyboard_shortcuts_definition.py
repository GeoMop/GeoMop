"""Keyboard shortcuts definition.
"""


DEFAULT_USER_SHORTCUTS = {
    # editor actions
    'undo': 'Ctrl+Z',
    'redo': 'Ctrl+Y',
    'comment': 'Ctrl+/',
    'show_autocompletion': 'Ctrl+Space',

    # menu actions
    'new_file': 'Ctrl+N',
    'open_file': 'Ctrl+O',
    'open_window': 'Ctrl+W',
    'save_file': 'Ctrl+S',
    'save_file_as': 'Ctrl+Shift+S',
    'import_file': 'Ctrl+I',
    'exit': 'Ctrl+Q',
    'find': 'Ctrl+F',
    'replace': 'Ctrl+H',
    'edit_format': 'Ctrl+E',
}
"""default keyboard shortcuts"""


SHORTCUT_LABELS = {
    # editor actions
    'undo': 'Undo an action',
    'redo': 'Redo an action',
    'comment': 'Toggle comment',
    'show_autocompletion': 'Display autocompletion options',

    # menu actions
    'new_file': 'New file',
    'open_file': 'Open file',
    'open_window': 'Open window',
    'save_file': 'Save file',
    'save_file_as': 'Save file as',
    'import_file': 'Import file',
    'exit': 'Quit application',
    'find': 'Find dialog',
    'replace': 'Replace dialog',
    'edit_format': 'Edit format file',
}
"""labels of shortcuts to be displayed in the user interface"""


SYSTEM_SHORTCUTS = {
    # editor actions
    'copy': 'Ctrl+C',
    'paste': 'Ctrl+V',
    'cut': 'Ctrl+X',
    'select_all': 'Ctrl+A',
    'unindent': 'Shift+Tab',
    'delete': 'Delete',
    'tab': 'Tab',
    'backspace': 'Backspace',
    'escape': 'Esc',
    'f3': 'F3',
}
"""system keyboard shortcuts that can not be changed by user"""


SCINTILLA_DISABLE = [
    'copy',
    'paste',
    'cut',
    'undo',
    'redo',
    'unindent',
    'comment',
    'delete',
    'select_all',
    'show_autocompletion',
]
"""shortcuts to be disabled in default scintilla behavior"""
