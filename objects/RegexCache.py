import regex


class RegexCache:

    def __init__(self, **key_pattern):
        self.key_pattern = key_pattern
        self.cache = {}

    def get_by_name(self, name) -> regex.Pattern:
        if name not in self.cache:
            self.cache[name] = regex.compile(self.key_pattern[name])
        return self.cache[name]

    def add_pater_name(self, name, pater):
        self.key_pattern[name] = pater

    def add_pattern_if_not_added(self, **args):
        for name, pattern in args.items():
            if name not in self.key_pattern:
                self.key_pattern[name] = pattern
