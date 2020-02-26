class Error(Exception):
    """Base class for exceptions in this module."""
    def __init__(self, message):
        self.message = message


class APIError(Error):
    """ Base class for API exceptions """


class NotFound(Error):
    pass


class InvalidArgument(Error):
    """ Exception for invalid command argument """
