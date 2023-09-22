from objects.CompilerErrorLevels import CompilerErrorLevels


class CompilerResult:

    def __init__(self, status: CompilerErrorLevels | None, message: str | None) -> None:
        self.message = message
        self.status = status
        self.messages: list[(CompilerErrorLevels, str)] = []

    @staticmethod
    def ok():
        return CompilerResult(CompilerErrorLevels.OK, "")

    @staticmethod
    def error(message: str):
        return CompilerResult(CompilerErrorLevels.ERROR, message)

    @staticmethod
    def warn(message: str):
        return CompilerResult(CompilerErrorLevels.WARNING, message)

    @staticmethod
    def info(message: str):
        return CompilerResult(CompilerErrorLevels.INFO, message)

    def accumulate(self, other):

        if other.status is None:
            return self
        if other.message_count() == 1:
            if self.status is None:
                self.status = other.status
                self.message = other.message
                return self

            if len(self.messages) == 0:
                self.messages.append((self.status, self.message))

            if other.status.is_severity_higher(self.status):
                self.status = other.status

                self.messages.append((other.status, other.message))
        else:
            for sev, msg in other.messages:
                if self.status is None:
                    self.status = sev
                    self.message = msg
                    continue

                if len(self.messages) == 0:
                    self.messages.append((sev, msg))

                if sev.is_severity_higher(self.status):
                    self.status = sev

                    self.messages.append((sev, msg))
        return self

    def message_count(self) -> int:
        return 1 if len(self.messages) == 0 else len(self.messages)

    def __str__(self) -> str:
        if self.message_count() == 1:
            return f"[{self.status}] {self.message}"
        else:
            res = ""
            for msg in self.messages:
                res += f"[{msg[0]}] {msg[1]}\n"
            return res

    @staticmethod
    def empty():
        return CompilerResult(None, None)

    def not_empty_or_ok(self):
        return self if self.status is not None else self.ok()
