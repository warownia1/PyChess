import sys

import itertools
import pygame
from pygame import Rect

from board import BoardManager
from locals import *


WINDOW_SIZE = 480, 480
BLACK_FIELD = [0x88, 0x66, 0x33]
WHITE_FIELD = [0xFF, 0xFF, 0xEE]
BOARD_POSITION = (48, 48)


pygame.init()

clock = pygame.time.Clock()
screen = pygame.display.set_mode(WINDOW_SIZE)
board_surface = pygame.Surface((384, 384))

pygame.display.set_caption('Chess Game')
print(pygame.display.Info())

sprites = pygame.image.load('ChessPiecesSprite.png').convert_alpha(screen)
piece_rects = {
    color: {
        piece: Rect(left, top, 48, 48)
        for piece, left in zip(
            [KING, QUEEN, BISHOP, KNIGHT, ROOK, PAWN], range(0, 288, 48)
        )
    }
    for color, top in [(WHITE, 0), (BLACK, 48)]
}

bm = BoardManager()


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        draw()

        clock.tick(30)


def draw():
    board_surface.fill(WHITE_FIELD)
    for (x, y) in itertools.product(range(8), repeat=2):
        if (x + y) % 2:
            field_rect = Rect(x * 48, y * 48, 48, 48)
            board_surface.fill(BLACK_FIELD, rect=field_rect)
    for piece in bm.board.white_pieces | bm.board.black_pieces:
        pos_x, pos_y = (piece.x - 1) * 48, (8 - piece.y) * 48
        board_surface.blit(
            sprites, (pos_x, pos_y), piece_rects[piece.color][piece.type]
        )
    screen.blit(board_surface, BOARD_POSITION)
    pygame.display.flip()

main()
