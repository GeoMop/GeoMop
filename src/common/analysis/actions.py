from common.analysis import base

class tuple(base._ActionBase):
    #__action_parameters = [('input', 'Any')]
    """ Merge any number of parameters into tuple."""
    def __init__(self, *inputs):
        super().__init__(inputs)

    def evaluate(self, inputs):
        return tuple(inputs)
