class ClassDictValidationError(Exception):
    pass


class CommandError(Exception):
    pass


class CommandFailureError(CommandError):
    pass
