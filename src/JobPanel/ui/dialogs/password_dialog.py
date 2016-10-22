"""
.. codeauthor:: Tomas Krizek <tomas.krizek1@tul.cz>
"""

from PyQt5 import QtWidgets


class SshPasswordDialog(QtWidgets.QDialog):
    """Dialog to enter shh password."""

    def __init__(self, parent, ssh):
        """Initializes the class."""
        super(SshPasswordDialog, self).__init__(parent)

        self.ssh = ssh

        message = "Please enter password for {name} ssh connection\n({user}@{host}:{port})"  .format(
            name=ssh.name,
            user=ssh.uid,
            host=ssh.host,
            port=ssh.port
        )
        self._connection_label = QtWidgets.QLabel(message, self)
        self._connection_label.setMinimumSize(85, 40)
        self._password_line_edit = QtWidgets.QLineEdit(self)
        self._password_line_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self._button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        self._button_box.accepted.connect(self.accept)

        # layout
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        main_layout.addWidget(self._connection_label)
        main_layout.addWidget(self._password_line_edit)
        main_layout.addWidget(self._button_box)

        self.setLayout(main_layout)

        # qt window settings
        self.setWindowTitle("Enter Password")

    @property
    def password(self):
        return self._password_line_edit.text()
