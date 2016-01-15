"""
JSON editor dialog.
"""
import os
import geomop_dialogs
from ui.template import EditorAppearance as appearance
import PyQt5.QtWidgets as QtWidgets
from PyQt5.Qsci import QsciScintilla, QsciLexerJavaScript

class JsonEditorDlg(QtWidgets.QDialog):
    """Dialog widget for JsonEditor."""

    def __init__(self, path, name, label_name, json, parent=None):
        super(JsonEditorDlg, self).__init__(parent)
        self.setWindowTitle("Json Editor")
        self._path = path
        self._name = name
        self._label_name = label_name
        self.orig_text = json

        self._label_file = QtWidgets.QLabel(label_name + ": " + name, self)
        self._save_button = QtWidgets.QPushButton("Save ...", self)
        self._save_button.clicked.connect(self._save_file)
        self._save_as_button = QtWidgets.QPushButton("Save as...", self)
        self._save_as_button.clicked.connect(self._save_as_file)
        self._cancel_button = QtWidgets.QPushButton("Cancel", self)
        self._cancel_button.clicked.connect(self._cancel)

        self._editor = QsciScintilla(self)

        # Set Yaml lexer
        self._editor.lexer = QsciLexerJavaScript()
        self._editor.setLexer(self._editor.lexer)
        self._editor.setMinimumSize(600, 450)
        self._editor.setText(json)
        
        appearance.set_default_appearence(self._editor)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self._label_file)
        button_layout.addWidget(self._save_button)
        button_layout.addWidget(self._save_as_button)
        button_layout.addWidget(self._cancel_button)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(button_layout)
        layout.addWidget(self._editor)
        self.setLayout(layout)

    def _save_file(self):
        """Save json file"""
        try:
            file_name = os.path.join(self._path, self._name + ".json")
            file_d = open(file_name, 'w')
            file_d.write(self._editor.text())
            file_d.close()
        except (RuntimeError, IOError) as err:
            err_dialog = geomop_dialogs.GMErrorDialog(self)
            err_dialog.open_error_dialog("Can't save file", err)

    def _save_as_file(self):
        """Save json file as"""
        file_name = os.path.join(self._path, self._name + ".json")
        json_file = QtWidgets.QFileDialog.getSaveFileName(
            self, "Set Json File", file_name, "Json Files (*.json)")
        if json_file[0]:
            new_name = os.path.split(json_file[0])[1][:-5]
            new_path = os.path.split(json_file[0])[0]
            self._name = new_name
            self._path = new_path
            self._label_file.setText(self._label_name + ": " + new_name)
            self._save_file()

    def _cancel(self):
        """Cancel dialog"""
        # ToDo:if is there chnges,  ask for save
        self.done(0)
