"""
Module contains widget that shows debug information.
"""

__author__ = 'Tomas Krizek'

# pylint: disable=invalid-name,no-member

from PyQt5.QtWidgets import QTextEdit


class DebugPanelWidget(QTextEdit):
    """Widget for displaying debug information."""

    def __init__(self, parent=None):
        """Initializes the class."""
        super(DebugPanelWidget, self).__init__(parent)
        self.setReadOnly(True)
        self.setFontFamily('Courier New')

    def show_data_node(self, node):
        """Displays debug information for `DataNode` node."""
        self.setText(DebugFormatter.data_node(node))


class DebugFormatter:
    """Class for formatting the debug information."""

    @staticmethod
    def data_node(node):
        """Returns debug string for `DataNode`."""
        if node is None:
            return "no node is set"

        text = (
            "{type_} at 0x{address:x}\n"
            "  key: {key_value}\n"
            "  key span: {key_span}\n"
            "  value span: {value_span}\n"
            "  parent: {parent}\n"
            "  ref: {ref}\n"
        )

        type_ = type(node).__name__
        address = id(node)
        key_span = "None"
        key_value = "None"
        value_span = node.span
        parent = "None"
        ref = node.ref

        if node.key is not None:
            if node.key.span is not None:
                key_span = node.key.span
            if node.key.value is not None:
                key_value = node.key.value

        if node.parent is not None:
            parent_format = "{name} ({type_} at 0x{address:x})"
            parent_type = type(node.parent).__name__
            parent_address = id(node.parent)
            if node.parent.key is not None and node.parent.key.value is not None:
                parent_name = node.parent.key.value
            else:
                parent_name = ""
            parent = parent_format.format(name=parent_name, type_=parent_type,
                                          address=parent_address)

        return text.format(
            type_=type_,
            address=address,
            key_value=key_value,
            key_span=key_span,
            value_span=value_span,
            parent=parent,
            ref=ref
        )
