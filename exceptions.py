class InvalidFieldError(Exception):
    pass


class IllegalMoveError(Exception):

    def __init__(self, message):
        self.message = message


class NoPieceError(Exception):
    pass


class InvalidPieceError(Exception):
    pass
