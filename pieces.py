import itertools
import math

from exceptions import InvalidFieldError
from locals import *


class Piece(object):

    def __init__(self, board, x, y, color, piece_type):
        self.captured = False
        self.board = board
        self.x = x
        self.y = y
        self.color = color
        self.type = piece_type

    def can_reach(self, x, y):
        """
        The base of movement checking for each piece.
        It checks if the piece doesn't leave the board, tries to move to the
        same field, or tries to step on the piece of the same color.
        This function should be invoked before more specific movement tests
        and, if it returns False, the final result must be False as well.
        :param x: x coordinate on the board
        :param y: y coordinate on the board
        :return: whether the target position is valid or not
        """
        if x <= 0 or y <= 0 or x > 8 or y > 8:
            # trying to get out of the board
            raise InvalidFieldError(x, y)
        if self.x == x and self.y == y:
            # moving to it's own field
            return False
        target_piece = self.board.get_piece(x, y)
        if target_piece is not None and target_piece.color == self.color:
            # trying to step on own piece
            return False
        return True

    def can_attack(self, x, y):
        """
        Checks if the piece can attack the specified square. Usually, if the
        field can be reached be a piece, it can also be attacked (with
        exception of pawns, which have different movement and attack).
        :param x: x coordinate of attacked field
        :param y: y coordinate of attacked fields
        :return: whether the field is attacked by the piece
        """
        return self.can_reach(x, y)

    def __repr__(self):
        return self.__class__.__name__


class King(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, KING)

    def can_reach(self, x, y):
        """
        Checks if the piece moved by one square only. x displacement and y
        displacement must be no more than 1
        """
        if not super().can_reach(x, y):
            return False
        return abs(self.x - x) <= 1 and abs(self.y - y) <= 1


class LineMovingPiece(Piece):

    def find_obstacles(self, x, y):
        dx = x - self.x
        dy = y - self.y
        x_list = (range(self.x, x, int(math.copysign(1, dx)))
                  if dx else itertools.repeat(x))
        y_list = (range(self.y, y, int(math.copysign(1, dy)))
                  if dy else itertools.repeat(y))
        for check_x, check_y in zip(x_list, y_list):
            if self.board.get_piece(check_x, check_y):
                return True
        return False


class Queen(LineMovingPiece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, QUEEN)

    def can_reach(self, x, y):
        """
        Checks if the target field is in the same rank, file or diagonal.
        """
        if not super().can_reach(x, y):
            return False
        dx = x - self.x
        dy = y - self.y
        if dx == 0 or dy == 0 or abs(dx) == abs(dy):
            if self.find_obstacles(x, y):
                return False
        else:
            return False
        return True


class Knight(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, KNIGHT)

    def can_reach(self, x, y):
        """
        Check if the piece moved two forward and one to the side.
        One coordinate displacement must be 1 while the other must be 2
        """
        if not super().can_reach(x, y):
            return False
        return (
            {abs(self.x - x), abs(self.y - y)} == {1, 2}
        )


class Rook(LineMovingPiece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, ROOK)

    def can_reach(self, x, y):
        """
        Check is the piece moved in a straight line along the file or rank.
        displacement in one coordinate is 0.
        """
        if not super().can_reach(x, y):
            return False
        dx = x - self.x
        dy = y - self.y
        if dx == 0 or dy == 0:
            if self.find_obstacles(x, y):
                return False
        else:
            return False
        return True


class Bishop(LineMovingPiece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, BISHOP)

    def can_reach(self, x, y):
        """
        Check is the movement is taken on the diagonal. Displacement in both
        coordinates should have the same absolute value.
        """
        if not super().can_reach(x, y):
            return False
        dx = x - self.x
        dy = y - self.y
        if abs(dx) == abs(dy):
            if self.find_obstacles(x, y):
                return False
        else:
            return False
        return True


class Pawn(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, PAWN)
        self.starting_rank = 2 if self.color == WHITE else 7

    def can_reach(self, x, y):
        """
        Check if the field the pawn is moving to is just in front of it.
        If it's in its starting position then two-fields move is allowed.
        """
        if not super().can_reach(x, y):
            return False
        if self.board.get_piece(x, y):
            return False
        forward = 1 if self.color == WHITE else -1
        if self.x - x == 0:
            if y == self.y + forward:
                return True
            if y == self.y + 2 * forward and self.starting_rank == self.y:
                return True
        return False

    def can_attack(self, x, y):
        """
        A specific mechanics for attacking with pawns. It can move in a
        straight line, but attack on diagonals only.
        :param x: x coordinate of attacked field
        :param y: y coordinate of attacked field
        :return: whether the field can be attacked by the pawn
        """
        forward = 1 if self.color == WHITE else -1
        if abs(x - self.x) == 1 and y == self.y + forward:
            # Pawn is moving forward along the diagonal.
            return True
        else:
            return False


class PhantomPawn(Piece):

    def __init__(self, board, x, y, color, pawn):
        super().__init__(board, x, y, color, None)
        self.linked_pawn = pawn