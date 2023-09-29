from objects.ArgumentSizeConstraint import ArgumentSizeConstraint
from objects.ArgumentTypes import ArgumentTypes


class InstructionArgument:
    def __init__(self, arg_type: ArgumentTypes, arg_size_constraint: list[ArgumentSizeConstraint] | None = None):
        self.arg_size_constraint = arg_size_constraint
        self.arg_type = arg_type

    type_size_support_info = {
        ArgumentTypes.LABEL: False,
        ArgumentTypes.NUMBER: True,
        ArgumentTypes.STRING: False,
        ArgumentTypes.REGISTER: True,
        ArgumentTypes.MEMORY_ADDRESS: True,
        ArgumentTypes.
    }
