"""Module with action error class."""


class ActionError(Exception):
    """Class for action standard error."""
    def __init__(self, code, message):
        super(ActionError, self).__init__(message)
        self.code = code
