import unittest.mock as mock
import pytest

from board import Board
from pieces import WHITE, BLACK, Piece, Rook


class TestRookMovement:

    @pytest.fixture()
    def empty_board(self):
        mock_board = mock.MagicMock(spec_set=Board)
        mock_board.get_piece.return_value = None
        return mock_board

    @pytest.fixture()
    def populated_board(self):
        mock_board = mock.MagicMock(spec=Board)
        mock_piece = mock.MagicMock(spec=Piece, color=WHITE)

        def mock_get_piece(x, y):
            if (x, y) in [(2, 5), (5, 7), (7, 5), (5, 3)]:
                return mock_piece
            else:
                return None

        mock_board.get_piece.side_effect = mock_get_piece
        return mock_board

    def test_allowed_move(self, empty_board):
        rook = Rook(empty_board, 5, 5, WHITE)
        assert rook.can_reach(5, 8)
        assert rook.can_reach(2, 5)
        assert rook.can_reach(7, 5)

    def test_illegal_move(self, empty_board):
        rook = Rook(empty_board, 5, 5, WHITE)
        assert not rook.can_reach(6, 6)
        assert not rook.can_reach(4, 3)

    def test_non_blocked_move(self, populated_board):
        rook = Rook(populated_board, 5, 5, WHITE)
        assert rook.can_reach(3, 5)
        assert rook.can_reach(6, 5)
        assert rook.can_reach(5, 6)

    def test_occupied_field_move(self, populated_board):
        rook = Rook(populated_board, 5, 5, WHITE)
        assert not rook.can_reach(2, 5)
        assert not rook.can_reach(5, 7)
        assert not rook.can_reach(7, 5)
        assert not rook.can_reach(5, 3)

    def test_blocked_field_moved(self, populated_board):
        rook = Rook(populated_board, 5, 5, WHITE)
        assert not rook.can_reach(1, 5)
        assert not rook.can_reach(5, 8)
        assert not rook.can_reach(8, 5)
        assert not rook.can_reach(5, 2)


class TestRookAttack:

    @pytest.fixture()
    def empty_board(self):
        mock_board = mock.MagicMock(spec_set=Board)
        mock_board.get_piece.return_value = None
        return mock_board

    @pytest.fixture()
    def populated_board(self):
        mock_board = mock.MagicMock(spec_set=Board)
        mock_white_piece = mock.MagicMock(spec=Piece, color=WHITE)
        mock_black_piece = mock.MagicMock(spec=Piece, color=BLACK)

        def mock_get_piece(x, y):
            if (x, y) in [(1, 3), (3, 1)]:
                return mock_white_piece
            if (x, y) in [(1, 6), (5, 1)]:
                return mock_black_piece
            return None

        mock_board.get_piece.side_effect = mock_get_piece
        return mock_board

    def test_blocked_capture(self, populated_board):
        rook = Rook(populated_board, 1, 1, WHITE)
        assert not rook.can_attack(1, 6)
        assert not rook.can_attack(5, 1)

    def test_allowed_capture(self, populated_board):
        rook = Rook(populated_board, 5, 6, WHITE)
        assert rook.can_attack(1, 6)
        assert rook.can_attack(5, 1)

    def test_attack_reach(self, empty_board):
        rook = Rook(empty_board, 4, 5, WHITE)
        assert rook.can_attack(7, 5)
        assert rook.can_attack(8, 5)
        assert rook.can_attack(4, 1)

    def test_unable_to_attack(self, empty_board):
        rook = Rook(empty_board, 5, 4, WHITE)
        assert not rook.can_attack(7, 5)
        assert not rook.can_attack(8, 5)
        assert not rook.can_attack(6, 3)
