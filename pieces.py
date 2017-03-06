import copy
import itertools
import math

from exceptions import IllegalMoveError
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
        self._board = board
        self.x = x
        self.y = y
        self.color = color
        self.type = piece_type

    def can_attack_field(self, x=None, y=None, fields=None):
        """
        Tells whether the piece can attack the specified field. If an iterable
        of fields is specified, the function returns True if at least one field
        can be attacked.
        :param x: target file
        :param y: target rank
        :param fields: list of fields to check
        :return: whether the field can be attacked
        """
        raise NotImplementedError

    def get_possible_moves(self):
        """
        Returns a set of all moves which are allowed for a given piece
        :return: list of all possible moves coordinates.
        :rtype: list[tuple[int, int]]
        """
        raise NotImplementedError

    def move(self, x, y):
        """
        Moves piece to a target field first checking if the move is allowed.
        :param x: target file
        :param y: target rank
        """
        if (x, y) in self.get_possible_moves():
            self.set_position(x, y)
        else:
            raise IllegalMoveError("Can't move the piece here.")

    def set_position(self, x, y):
        """
        Basic piece movement algorithm, picks the piece from the board and
        places it in a new location without checking move validity.
        :param x: target file
        :param y: target rank
        """
        self._board.move_piece(self, x, y)
        self.x, self.y = x, y

    def check_move(self, to_x, to_y):
        """
        Checks if the specified move is legal and does not result in check
        for your king.
        :param to_x: rank of the target field
        :param to_y: file of the target field
        :return: whether the move is legal
        """
        board = copy.deepcopy(self._board)
        piece = board.get_piece(self.x, self.y)
        board.move_piece(piece, to_x, to_y)
        piece.set_position(to_x, to_y)
        king = next(
            p for p in board.get_pieces(color=piece.color) if p.type == KING
        )
        for opp_piece in board.get_pieces(color=piece.opp_color):  # type: Piece
            if opp_piece.can_attack_field(king.x, king.y):
                return False
        return True

    @property
    def opp_color(self):
        """
        Returns the color of the pieces of the opponent.
        """
        return WHITE if self.color == BLACK else BLACK

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, self.x, self.y)


class King(Piece):
    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, KING)
        self._castle_available = True

    def can_attack_field(self, x=None, y=None, fields=None):
        """
        Checks if the fields lie next to the King.
        """
        if fields is None:
            fields = [(x, y)]
        for x, y in fields:
            if (abs(self.x - x) <= 1 and abs(self.y - y) <= 1 and
                    (x != self.x or y != self.y)):
                return True
        return False

    def get_possible_moves(self):
        moves = set()
        if self.can_castle('long'):
            moves.add((self.x - 2, self.y))
        if self.can_castle('short'):
            moves.add((self.x + 2, self.y))
        for dx, dy in itertools.product([-1, 0, 1], repeat=2):
            # eliminate case, when piece is not moving
            if dx == 0 and dy == 0:
                continue
            (x, y) = (self.x + dx, self.y + dy)
            # eliminate case when it goes out of the board
            if x >= 8 or y >= 8 or x < 0 or y < 0:
                continue
            # eliminate case when it steps on own piece
            target_piece = self._board.get_piece(x, y)
            if target_piece and target_piece.color == self.color:
                continue
            # check if the move is allowed and doesn't result in check
            if self.check_move(x, y):
                moves.add((x, y))
        return moves

    def can_castle(self, castle_type):
        """
        Tells if the long or short castle is possible.
        :param castle_type: type of castle to check, either "short" or "long"
        :return: whether the castle can be performed
        """
        assert castle_type == 'long' or castle_type == 'short'
        if not self._castle_available:
            # can't castle if not available
            return False
        # check if the piece in the corner is a rook and it can castle
        rook = (self._board.get_piece(0, self.y) if castle_type == 'long'
                else self._board.get_piece(7, self.y))  # type: Rook
        if not (isinstance(rook, Rook) and rook.can_castle):
            return False
        # get all fields between the king and the rook (excluding rook)
        path = [(x, self.y) for x in range(self.x, rook.x)]
        # can't castle if there is a piece in between
        if any(self._board.get_piece(fields=path[1:])):
            return False
        # can't castle if any of the fields the king crosses is attacked
        for opp_piece in self._board.get_pieces(color=self.opp_color):
            if opp_piece.can_attack_field(fields=path[:3]):
                return False
        return True

    def set_position(self, to_x, to_y):
        if (self._castle_available and abs(to_x - self.x) == 2
                and to_y - self.y == 0):
            rook = (self._board.get_piece(0, self.y) if to_x - self.x == -2
                    else self._board.get_piece(7, self.y))
            rook.set_position(
                self.x + int(math.copysign(1, to_x - self.x)), self.y)
        self._castle_available = False
        return super().set_position(to_x, to_y)


class LineMovementMixin:
    x = None
    y = None
    color = None
    _board = None

    def _possible_moves(self):
        """
        Returns all possible moves in a straight lines from the location of
        the piece.
        :return:
        :rtype: set[tuple[int, int]]
        """
        fields = set()

        def check_and_add(to_x, to_y):
            """
            Checks if the field can be reached and adds it to the set of fields.
            Returns True if the iteration should be stopped and the piece is
            blocked. When encountering own pieces, iteration stops before them,
            for opponent pieces, iteration stops on them
            :param to_x:
            :param to_y:
            :return: whether the iteration should be stopped
            """
            piece = self._board.get_piece(to_x, to_y)
            if piece is None:
                fields.add((to_x, to_y))
            elif piece.color != self.color:
                fields.add((to_x, to_y))
                return True
            elif piece.color == self.color:
                return True

        for x in range(self.x - 1, -1, -1):
            if check_and_add(x, self.y):
                break
        for x in range(self.x + 1, 8):
            if check_and_add(x, self.y):
                break
        for y in range(self.y - 1, -1, -1):
            if check_and_add(self.x, y):
                break
        for y in range(self.y + 1, 8):
            if check_and_add(self.x, y):
                break
        return fields


class DiagonalMovementMixin:
    x = None
    y = None
    color = None
    _board = None

    def _possible_moves(self):
        fields = set()

        def check_and_add(to_x, to_y):
            """
            Checks if the field can be reached and adds it to the set of fields.
            Returns True if the iteration should be stopped and the piece is
            blocked. When encountering own pieces, iteration stops before them,
            for opponent pieces, iteration stops on them
            :param to_x:
            :param to_y:
            :return: whether the iteration should be stopped
            """
            piece = self._board.get_piece(to_x, to_y)
            if piece is None:
                fields.add((to_x, to_y))
            elif piece.color != self.color:
                fields.add((to_x, to_y))
                return True
            elif piece.color == self.color:
                return True

        for (x, y) in zip(range(self.x + 1, 8), range(self.y + 1, 8)):
            if check_and_add(x, y):
                break
        for (x, y) in zip(range(self.x + 1, 8), range(self.y - 1, -1, -1)):
            if check_and_add(x, y):
                break
        for (x, y) in zip(range(self.x - 1, -1, -1), range(self.y + 1, 8)):
            if check_and_add(x, y):
                break
        for (x, y) in zip(range(self.x - 1, -1, -1),
                          range(self.y - 1, -1, -1)):
            if check_and_add(x, y):
                break
        return fields


class Queen(DiagonalMovementMixin, LineMovementMixin, Piece):
    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, QUEEN)

    def can_attack_field(self, x=None, y=None, fields=None):
        moves = DiagonalMovementMixin._possible_moves(self)
        moves.update(LineMovementMixin._possible_moves(self))
        if fields is None:
            fields = [(x, y)]
        return bool(moves.intersection(fields))

    def get_possible_moves(self):
        moves = DiagonalMovementMixin._possible_moves(self)
        moves.update(LineMovementMixin._possible_moves(self))
        return {move for move in moves if self.check_move(*move)}


class Rook(LineMovementMixin, Piece):
    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, ROOK)
        self._can_castle = True

    @property
    def can_castle(self):
        return self._can_castle

    def can_attack_field(self, x=None, y=None, fields=None):
        moves = self._possible_moves()
        if fields is None:
            fields = [(x, y)]
        return bool(moves.intersection(fields))

    def get_possible_moves(self):
        return {move for move in self._possible_moves()
                if self.check_move(*move)}

    def set_position(self, to_x, to_y):
        self._can_castle = False
        return super().set_position(to_x, to_y)


class Bishop(DiagonalMovementMixin, Piece):
    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, BISHOP)

    def can_attack_field(self, x=None, y=None, fields=None):
        moves = self._possible_moves()
        if fields is None:
            fields = [(x, y)]
        return bool(moves.intersection(fields))

    def get_possible_moves(self):
        return {move for move in self._possible_moves()
                if self.check_move(*move)}


class Knight(Piece):
    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, KNIGHT)

    def can_attack_field(self, x=None, y=None, fields=None):
        if fields is None:
            fields = [(x, y)]
        for (x, y) in fields:
            if {abs(x - self.x), abs(y - self.y)} == {1, 2}:
                return True
        return False

    def get_possible_moves(self):
        moves = set(itertools.chain(
            itertools.product([self.x - 2, self.x + 2],
                              [self.y - 1, self.y + 1]),
            itertools.product([self.x - 1, self.x + 1],
                              [self.y - 2, self.y + 2])
        ))
        return {
            (x, y) for (x, y) in moves
            if (0 <= x < 8 and 0 <= y < 8 and
                (self._board.get_piece(x, y) is None or
                    self._board.get_piece(x, y).color != self.color) and
                self.check_move(x, y))
        }


# noinspection SpellCheckingInspection
class Pawn(Piece):
    def __init__(self, board, x, y, color):
        super().__init__(board, x, y, color, PAWN)
        self._starting_rank = 1 if self.color == WHITE else 6
        self._forward = 1 if self.color == WHITE else -1
        self._en_passant = False

    def can_attack_field(self, x=None, y=None, fields=None):
        if fields is None:
            fields = [(x, y)]
        return bool(self.attacked_fields.intersection(fields))

    def get_possible_moves(self):
        moves = set()
        for pos in self.attacked_fields:
            piece = self._board.get_piece(*pos)
            if piece is None:
                # if no piece on the attacked field, en-passant may be possible
                piece = self._board.get_piece(pos[0], self.y)  # type: Pawn
                if (isinstance(piece, Pawn) and
                        piece.color == self.opp_color and
                        piece._en_passant):
                    moves.add(pos)
            elif piece.color == self.opp_color:
                moves.add(pos)
        fields_ahead = self._board.get_piece(
            fields=[(self.x, self.y + self._forward),
                    (self.x, self.y + self._forward * 2)]
        )
        if self.y == self._starting_rank and not any(fields_ahead):
            moves.add((self.x, self.y + self._forward * 2))
        if fields_ahead[0] is None:
            moves.add((self.x, self.y + self._forward))
        return {move for move in moves if self.check_move(*move)}

    # todo: reaching the last rank results in: list index out of range
    @property
    def attacked_fields(self):
        fields = set()
        if 7 > self.y + self._forward > 0:
            if self.x > 0:
                fields.add((self.x - 1, self.y + self._forward))
            if self.x < 7:
                fields.add((self.x + 1, self.y + self._forward))
        return fields

    def set_position(self, x, y):
        if abs(y - self.y) == 2:
            self._en_passant = True
        elif ((x, y) in self.attacked_fields and
                self._board.get_piece(x, y) is None):
            pawn = self._board.get_piece(x, self.y)
            assert isinstance(pawn, Pawn) and pawn.en_passant
            self._board.remove_piece(pawn)
        return super().set_position(x, y)

    @property
    def en_passant(self):
        return self._en_passant
