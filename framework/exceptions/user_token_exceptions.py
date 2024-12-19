
class TokenExpiredException(Exception):
    """Exception raised match request is not found.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class TokenNotValidException(Exception):
    """Exception raised when the match request is not active.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)