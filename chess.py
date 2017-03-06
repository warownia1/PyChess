import itertools
import sys

import pygame
from pygame import Rect

from board import BoardManager
from exceptions import ChessException
from locals import *
from panel import Panel


WINDOW_SIZE = 480, 480
BLACK_FIELD = [0x88, 0x66, 0x33]
WHITE_FIELD = [0xFF, 0xFF, 0xEE]
SELECTED_FIELD_COLOR = [0xEE, 0xEE, 0x55]
BOARD_POSITION = Rect(48, 48, 384, 384)


pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()
pygame.display.set_caption('Chess Game')


class WindowPanel(Panel):
    pass


class BoardPanel(Panel):

    _sprites = pygame.image.load('ChessPiecesSprite.png').convert_alpha(screen)
    _piece_sprite_rects = {
        color: {
            piece: Rect(left, top, 48, 48)
            for piece, left in zip(
                [KING, QUEEN, BISHOP, KNIGHT, ROOK, PAWN], range(0, 288, 48)
            )
        }
        for color, top in [(WHITE, 0), (BLACK, 48)]
    }

    def __init__(self):
        super(BoardPanel, self).__init__(BOARD_POSITION)
        self._selected_field = None

    def paint(self, surface):
        surface.fill(WHITE_FIELD)
        for (x, y) in itertools.product(range(8), repeat=2):
            if (x + y) % 2:
                field_rect = Rect(x * 48, y * 48, 48, 48)
                surface.fill(BLACK_FIELD, rect=field_rect)
        if self._selected_field:
            field_rect = Rect(self._selected_field[0] * 48,
                              (7 - self._selected_field[1]) * 48,
                              48, 48)
            surface.fill(SELECTED_FIELD_COLOR, field_rect)
        for piece in bm.board.get_pieces():
            pos_x, pos_y = piece.x * 48, (7 - piece.y) * 48
            surface.blit(
                self._sprites, (pos_x, pos_y),
                self._piece_sprite_rects[piece.color][piece.type]
            )

    def on_click(self, x, y):
        clicked_field = (x // 48, 7 - y // 48)
        if self._selected_field is None:
            self._selected_field = clicked_field
        else:
            try:
                bm.move_piece(self._selected_field[0], self._selected_field[1],
                              clicked_field[0], clicked_field[1])
            except ChessException as e:
                print(e, file=sys.stderr)
            self._selected_field = None


window_panel = WindowPanel(Rect((0, 0), WINDOW_SIZE), screen)
window_panel.add_component(BoardPanel())

bm = BoardManager()


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                window_panel.clicked(*event.pos)

        window_panel.repaint()
        pygame.display.flip()
        clock.tick(30)

main()
