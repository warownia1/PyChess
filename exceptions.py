class ChessException(Exception):
    pass


class InvalidFieldError(ChessException):
    pass


class IllegalMoveError(ChessException):

    def __init__(self, message):
        self.message = message


class NoPieceError(ChessException):
    pass


class InvalidPieceError(ChessException):
    pass
