import itertools
import math

from exceptions import InvalidFieldError, IllegalMoveError
from locals import *


class Piece(object):
    """
    :type board: board.Board
    :type x: int
    :type y: int
    :type color: str
    :type type: str
    """

    def __init__(self, board, x, y, color, piece_type):
        """
        :param board: board the piece is placed on
        :param x: initial file where the piece is placed
        :param y: initial rank there the piece is places
        :param color: side the piece is on
        :param piece_type: type of the piece, for fast recognition
        """
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

    def move_piece(self, to_x, to_y):
        """
        Basic piece movement algorithm, picks the piece from the board and
        places it in a new location.
        :param to_x: target file
        :param to_y: target rank
        """
        target_field = self.board.get_piece(to_x, to_y)
        if target_field is None:
            if self.can_reach(to_x, to_y):
                self.board.pick_piece(self)
                self.board.put_piece(self, to_x, to_y)
            else:
                raise IllegalMoveError("Can't reach the field")
        elif target_field.color != self.color:
            if self.can_attack(to_x, to_y):
                self.board.remove_piece(target_field)
                self.board.pick_piece(self)
                self.board.put_piece(self, to_x, to_y)
            else:
                raise IllegalMoveError("Can't attack the field")
        else:
            raise IllegalMoveError("Field is occupied")

    @property
    def opp_color(self):
        """
        Returns the color of the pieces of the opponent.
        """
        return WHITE if self.color == BLACK else BLACK

    def __repr__(self):
        return self.__class__.__name__


class King(Piece):

    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, KING)

    def can_reach(self, x, y):
        """
        Checks if the piece moved by one square only. x displacement and y
        displacement must be no more than 1.
        Extra check is performed in case of castling.
        Checks if the destination field is not attacked by opponent pieces.
        """
        if not super().can_reach(x, y):
            return False
        # long castle must be allowed
        # displacement vector of the piece is [-2, 0]
        # none of the fields in between can be attacked
        if (self.board.long_castle_allowed[self.color] and
                x - self.x == -2 and y == self.y and
                self.board.is_field_attacked(
                    self.opp_color, fields=[(x, y), (x - 1, y), (x - 2, y)]
                )):
            rook = self.board.get_piece(1, y)
            assert rook is not None
            return rook.can_reach(x - 1, y)
        return (abs(self.x - x) <= 1 and
                abs(self.y - y) <= 1 and
                not self.board.is_field_attacked(self.opp_color, x, y))


class LineMovingPiece(Piece):

    def find_obstacles(self, x, y):
        """
        Finds if any piece is blocking the way to the point (x, y) in a
        straight line or diagonal.
        :param x: destination x coordinate (exclusive)
        :param y: destination y coordinate (exclusive)
        :return: whether the obstacle was find on the way
        """
        dx = x - self.x
        dy = y - self.y
        if dx == 0 and dy == 0:
            return False
        dir_x = int(math.copysign(1, dx))
        x_list = (range(self.x + dir_x, x, dir_x)
                  if dx else itertools.repeat(x))
        dir_y = int(math.copysign(1, dy))
        y_list = (range(self.y + dir_y, y, dir_y)
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
        return (
            not super().can_reach(x, y) and
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
