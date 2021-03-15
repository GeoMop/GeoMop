from PyQt5.QtGui import QValidator


class NameValidator(QValidator):
    def __init__(self, is_text_unique_fnc, default_text_fnc, on_fixup_fnc=lambda default: None):
        """ Text validator which only accepts unique text. Derived from QValidator https://doc.qt.io/qt-5/qvalidator.html
            Unique text is defined by parameter is_text_unique_fnc. function that takes string and return whether it is unique
            is_text_unique_fnc: Function that takes string and return whether it is unique.
            default_text_fnc: Function which returns original or default text.
            on_fixup_fnc: Callback which takes fixed string and makes appropriate actions to react to that change."""
        super(NameValidator, self).__init__()
        self.is_text_unique_fnc = is_text_unique_fnc
        self.default_text_fnc = default_text_fnc
        self.on_fixup_fnc = on_fixup_fnc

    def validate(self, input: str, pos: int):
        """Needed for QValidator, defines what is considered valid name."""
        if self.is_text_unique_fnc(input) or self.default_text_fnc() == input:
            return QValidator.Acceptable, input, pos
        else:
            return QValidator.Intermediate, input, pos

    def fixup(self, a0: str) -> str:
        """If user enters invalid name change it back to the original name."""
        default = self.default_text_fnc()
        self.on_fixup_fnc(default)
        return default
