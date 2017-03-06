import sys

import colorama

from exceptions import NoPieceError, InvalidPieceError
from locals import *
from pieces import Piece, King, Queen, Knight, Rook, Bishop, Pawn

colorama.init(autoreset=True)


class BoardManager(object):

    def __init__(self):
        self.board = Board()
        self.player_to_move = WHITE

    def move_piece(self, from_x, from_y, to_x, to_y):
        """
        Takes two pairs of tuples with fields coordinates and move the piece
        from one square to another.
        :param from_x: coordinate where the piece is picked from
        :param from_y: coordinates where piece is picked from
        :param to_x: coordinate where the piece is moved to
        :param to_y: coordinates where the piece is moved to
        :raises InvalidFieldError: one of the fields does not exist
        :raises InvalidPieceError: selected piece cannot be picked
        :raises NoPieceError: there is no piece on the origin square
        :raises IllegalMoveError: specified move is not valid
        """
        piece = self.board.get_piece(from_x, from_y)
        if piece is None:
            raise NoPieceError("There is no piece here")
        if piece.color != self.player_to_move:
            raise InvalidPieceError("You don't own this piece")
        piece.move(to_x, to_y)
        self.switch_player()

    def switch_player(self):
        self.player_to_move = WHITE if self.player_to_move == BLACK else BLACK


class Board(object):

    def __init__(self):
        self._fields = [[None for _ in range(8)] for _ in range(8)]
        self._fill_starting_board()

    def _fill_starting_board(self):
        """
        Create all pieces and set them to their starting positions.
        """
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for x, piece_cls in enumerate(pieces):
            piece = piece_cls(self, x, 0, WHITE)
            self._fields[0][x] = piece

            piece = Pawn(self, x, 1, WHITE)
            self._fields[1][x] = piece

            piece = piece_cls(self, x, 7, BLACK)
            self._fields[7][x] = piece

            piece = Pawn(self, x, 6, BLACK)
            self._fields[6][x] = piece

    def get_pieces(self, color=None):
        """
        Returns all the pieces currently placed on the board
        :param color: color of the pieces to fetch or None for all
        :return: iterable of all pieces
        :rtype: collections.Iterable[Piece]
        """
        assert color in {None, WHITE, BLACK}
        flattened_fields = (
            piece for row in self._fields for piece in row if piece)
        if color == WHITE:
            return (p for p in flattened_fields if p.color == WHITE)
        elif color == BLACK:
            return (p for p in flattened_fields if p.color == BLACK)
        else:
            return flattened_fields

    def get_piece(self, x=None, y=None, fields=None):
        """
        Gets the piece standing on the given field.
        :param x: file of the field
        :param y: rank of the field
        :param fields: list of fields coordinates
        :return: piece standing on the field
        :rtype: Piece | list[Piece]
        """
        assert (x is not None and y is not None) != (fields is not None)
        if fields is not None:
            return [self._fields[y][x] for (x, y) in fields]
        else:
            return self._fields[y][x]

    def pick_piece(self, piece):
        """
        Picks the piece from the board and leave an empty field.
        :param piece: piece to be picked
        """
        x, y = piece.x, piece.y
        assert self._fields[y][x] == piece, 'This piece is not there'
        self._fields[y][x] = None

    def put_piece(self, piece, x, y):
        """
        Places the piece on the field in the given position.
        :param piece: piece to be placed
        :param x: file of the field
        :param y: rank of the field
        """
        piece.x, piece.y = (x, y)
        self._fields[y][x] = piece

    def remove_piece(self, piece):
        """
        Removes the piece from the board.
        :param piece: piece to be removed
        :type piece: Piece
        """
        self._fields[piece.y][piece.x] = None

    def move_piece(self, piece, to_x, to_y):
        """
        Moves the piece on the board using pick_piece and put_piece methods.
        :param piece: piece to move
        :param to_x:
        :param to_y:
        :return:
        """
        self.pick_piece(piece)
        self.put_piece(piece, to_x, to_y)

    def print(self):
        """
        Print the board to console output.
        """
        print('  |  0 1 2 3 4 5 6 7')
        print('--+-----------------')
        for y, rank in zip(range(7, -1, -1), reversed(self._fields)):
            sys.stdout.write('%i |  ' % y)
            for x, piece in enumerate(rank):
                back_color = (colorama.Back.RED
                              if (x + y) % 2 == 0
                              else colorama.Back.LIGHTYELLOW_EX)
                if piece is None:
                    sys.stdout.write(back_color + '  ')
                else:
                    front_color = (colorama.Fore.BLACK
                                   if piece.color == BLACK
                                   else colorama.Fore.WHITE)
                    sys.stdout.write(back_color + front_color +
                                     piece.type + ' ')
            sys.stdout.write('\n')
