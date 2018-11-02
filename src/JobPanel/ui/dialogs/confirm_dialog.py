"""Dialog for confirmation of multiple actions e.g. deleting multiple MJ
.. codeauthor:: Tomas Blazek <tomas.blazek@tul.cz>
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QDialogButtonBox, QLabel, QListWidget,QListWidgetItem)


def ConfirmDialog(selected_items, message, parent = None, title="Confirm Action"):
    """Creates dialog for confirming multiple action
        :param selected_items: list of selected QTreeWidgetItems from Overview
        :param message: message for user
        :param parent: parent widget of this dialog
        :param title: title of dialog window
        :return dialog
    """
    dialog = QDialog(parent)

    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)

    label = QLabel(message)
    label.setWordWrap(True)
    list = QListWidget()
    for item in selected_items:
        QListWidgetItem("MultiJob: " + item.text(2) + "\t" + "From Analysis: " + item.text(1), list)
    list.setSelectionMode(list.NoSelection)


    main_layout = QVBoxLayout()
    main_layout.addWidget(label)
    main_layout.addWidget(list)
    main_layout.addWidget(button_box)

    dialog.setLayout(main_layout)

    dialog.setWindowTitle(title)
    dialog.setMinimumSize(300, 150)
    dialog.resize(400,300)
    return dialog
