from objects.ArgumentSize import ArgumentSize


class ArgumentSizeConstraint:
    def __init__(self, valid_list: list[ArgumentSize]):
        self.valid_list = valid_list
        self.applyed_contraints = []

    @staticmethod

    
    def validate_size(self, size: ArgumentSize):
        if self.is_any:
            return True
        if self.is_exact:
            return size == self.options_min_any
        if self.is_range:
            return self.__is_in_range(size)
        if self.is_options:
            return size in self.options_min_any
        return False

    def __is_in_range(self, size: ArgumentSize):
        if ArgumentSize.is_signed(size):
            return ArgumentSize.get_size(self.options_min_any)\
                <= ArgumentSize.get_size(size)\
                <= ArgumentSize.get_size(self.max_any)
        else:
            return ArgumentSize.get_size(self.options_min_any)\
                < ArgumentSize.get_size(size)\
                <= ArgumentSize.get_size(self.max_any)
