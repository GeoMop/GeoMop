from PyQt5.QtGui import QValidator


class TextValidator(QValidator):
    def __init__(self, is_text_unique_fnc, default_text_fnc, on_fixup_fnc=lambda default: None):
        """ Text validator which only accepts unique text.
            Unique text is defined by parameter is_text_unique_fnc. function that takes string and return wheater it is unique
            is_text_unique_fnc: Function that takes string and return whether it is unique.
            default_text_fnc: Function which returns original or default text.
            on_fixup_fnc: Function which takes fixed string and makes appropriate actions to react to that change."""
        super(TextValidator, self).__init__()
        self.is_text_unique_fnc = is_text_unique_fnc
        self.default_text_fnc = default_text_fnc
        self.on_fixup_fnc = on_fixup_fnc

    def validate(self, input: str, pos: int):
        if self.is_text_unique_fnc(input) or self.default_text_fnc() == input:
            return QValidator.Acceptable, input, pos
        else:
            return QValidator.Intermediate, input, pos

    def fixup(self, a0: str) -> str:
        default = self.default_text_fnc()
        self.on_fixup_fnc(default)
        return default
