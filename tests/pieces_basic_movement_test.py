import unittest.mock as mock

from chess import Board
from pieces import WHITE, BLACK, King, Queen, Knight, Rook, Bishop, Pawn

mock_board = mock.MagicMock(spec_set=Board)
mock_board.get_piece.return_value = None


def test_king_reach():
    king = King(mock_board, 5, 5, WHITE)
    assert king.can_reach(6, 6)
    assert king.can_reach(4, 5)
    assert king.can_reach(5, 4)
    assert not king.can_reach(5, 3)
    assert not king.can_reach(3, 5)
    assert not king.can_reach(1, 1)


def test_queen_reach():
    queen = Queen(mock_board, 5, 5, WHITE)
    assert queen.can_reach(6, 6)
    assert queen.can_reach(8, 8)
    assert queen.can_reach(1, 5)
    assert queen.can_reach(7, 3)
    assert queen.can_reach(5, 8)
    assert not queen.can_reach(6, 8)
    assert not queen.can_reach(2, 1)


def test_knight_reach():
    knight = Knight(mock_board, 5, 5, WHITE)
    assert knight.can_reach(7, 4)
    assert knight.can_reach(3, 4)
    assert knight.can_reach(4, 7)
    assert not knight.can_reach(6, 5)
    assert not knight.can_reach(4, 4)
    assert not knight.can_reach(1, 1)

    knight = Knight(mock_board, 2, 1, WHITE)
    assert not knight.can_reach(2, 3)


def test_rook_reach():
    rook = Rook(mock_board, 5, 5, WHITE)
    assert rook.can_reach(5, 8)
    assert rook.can_reach(2, 5)
    assert rook.can_reach(7, 5)
    assert not rook.can_reach(6, 6)
    assert not rook.can_reach(4, 3)


def test_bishop_reach():
    bishop = Bishop(mock_board, 5, 5, WHITE)
    assert bishop.can_reach(7, 7)
    assert bishop.can_reach(1, 1)
    assert bishop.can_reach(2, 8)
    assert not bishop.can_reach(7, 8)
    assert not bishop.can_reach(1, 2)
    assert not bishop.can_reach(6, 5)


def test_white_pawn_reach():
    pawn = Pawn(mock_board, 5, 5, WHITE)
    assert pawn.can_reach(5, 6)
    assert not pawn.can_reach(6, 5)
    assert not pawn.can_reach(5, 4)
    assert not pawn.can_reach(5, 7)


def test_white_pawn_initial_reach():
    pawn = Pawn(mock_board, 4, 2, WHITE)
    assert pawn.can_reach(4, 4)
    assert pawn.can_reach(4, 3)
    assert not pawn.can_reach(4, 1)


def test_black_pawn_reach():
    pawn = Pawn(mock_board, 6, 2, BLACK)
    assert pawn.can_reach(6, 1)
    assert not pawn.can_reach(5, 2)
    assert not pawn.can_reach(6, 3)


def test_black_pawn_initial_reach():
    pawn = Pawn(mock_board, 5, 7, BLACK)
    assert pawn.can_reach(5, 5)
    assert pawn.can_reach(5, 6)
    assert not pawn.can_reach(5, 8)
    assert not pawn.can_reach(5, 4)
