import colorama
import sys

from exceptions import InvalidFieldError, NoPieceError, InvalidPieceError
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
            raise NoPieceError
        if piece.color != self.player_to_move:
            raise InvalidPieceError
        piece.move_piece(to_x, to_y)
        self.switch_player()

    def switch_player(self):
        self.player_to_move = WHITE if self.player_to_move == BLACK else BLACK


class Board(object):

    def __init__(self):
        self.fields = [[None for _ in range(8)] for _ in range(8)]
        self.black_pieces = set()
        self.white_pieces = set()
        self.white_king = None
        self.black_king = None
        self._fill_starting_board()
        self.long_castle_allowed = {
            WHITE: True,
            BLACK: True
        }
        self.short_castle_allowed = {
            WHITE: True,
            BLACK: True
        }

    def _fill_starting_board(self):
        """
        Create all pieces and set them to their starting positions.
        """
        pieces = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for x, piece_cls in enumerate(pieces):
            piece = piece_cls(self, x + 1, 1, WHITE)
            if piece_cls == King:
                self.white_king = piece
            self.white_pieces.add(piece)
            self.fields[0][x] = piece

            piece = Pawn(self, x + 1, 2, WHITE)
            self.fields[1][x] = piece
            self.white_pieces.add(piece)

            piece = piece_cls(self, x + 1, 8, BLACK)
            if piece_cls == King:
                self.black_king == piece
            self.fields[7][x] = piece
            self.black_pieces.add(piece)

            piece = Pawn(self, x + 1, 7, BLACK)
            self.fields[6][x] = piece
            self.black_pieces.add(piece)

    def get_piece(self, x, y):
        """
        Gets the piece standing on the given field.
        :param x: file of the field
        :param y: rank of the field
        :return: piece standing on the field
        :rtype: Piece
        """
        if x <= 0 or x > 8 or y <= 0 or y > 8:
            raise InvalidFieldError
        return self.fields[y - 1][x - 1]

    def pick_piece(self, piece):
        """
        Picks the piece from the board and leave an empty field.
        :param piece: piece to be picked
        """
        x, y = piece.x, piece.y
        self.fields[y - 1][x - 1] = None

    def put_piece(self, piece, x, y):
        """
        Places the piece on the field in the given position.
        :param piece: piece to be placed
        :param x: file of the field
        :param y: rank of the field
        """
        piece.x, piece.y = (x, y)
        self.fields[y - 1][x - 1] = piece

    def remove_piece(self, piece):
        """
        Removes the piece from the board.
        :param piece: piece to be removed
        :type piece: Piece
        """
        piece = self.fields[piece.y - 1][piece.x - 1]
        pieces_set = self.white_pieces \
            if piece.color == WHITE else self.black_pieces
        pieces_set.remove(piece)
        self.fields[piece.y - 1][piece.x - 1] = None

    def is_king_in_check(self, color):
        """
        Tells whether the king of the specified color is in check.
        Checks all opponent's pieces performing check of attack on king's
        field.
        :param color: piece color to be checked
        :return: whether the king is checked
        """
        assert color in {WHITE, BLACK}
        pieces_color, king = (
            (BLACK, self.white_king)
            if color == WHITE
            else (self.white_pieces, self.black_king)
        )
        return self.is_field_attacked(pieces_color, king.x, king.y)

    def is_field_attacked(self, color, x=None, y=None, fields=None):
        """
        Tells whether the field is attacked by the pieces of the specified
        color.
        :param color: color of pieces to examine
        :param x: file of the examined field
        :param y: rank of the examined field
        :param fields: list of tuple containing coordinates of fields to check
        :return: whether the field is under attack
        """
        assert color in (WHITE, BLACK)
        assert (x and y) or fields
        if fields is None:
            fields = [(x, y)]
        pieces = (
            self.white_pieces if color == WHITE else self.black_pieces
        )
        for piece in pieces:
            for x, y in fields:
                if piece.can_attack(x, y):
                    return True
        return False

    def print(self):
        """
        Print the board to console output.
        """
        print('  |  1 2 3 4 5 6 7 8')
        print('--+-----------------')
        for y, rank in zip(range(7, -1, -1), reversed(self.fields)):
            sys.stdout.write('%i |  ' % (y + 1))
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
