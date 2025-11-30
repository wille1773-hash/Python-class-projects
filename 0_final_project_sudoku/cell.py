"""Cell representation for the Sudoku board."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
SLATE = (60, 60, 60)
SKETCH_GRAY = (140, 140, 140)
SELECTED = (214, 120, 81)
LOCKED_BG = (238, 238, 238)


@dataclass
class FontBundle:
    value_font: pygame.font.Font
    sketch_font: pygame.font.Font


class Cell:
    """Represents a single square within the Sudoku board."""

    def __init__(
        self,
        value: int,
        row: int,
        col: int,
        size: int,
        screen: pygame.Surface,
        fonts: FontBundle,
        locked: bool = False,
    ) -> None:
        self.value = value
        self.row = row
        self.col = col
        self.size = size
        self.screen = screen
        self.fonts = fonts
        self.locked = locked
        self.sketched_value = 0
        self.selected = False

    def set_cell_value(self, value: int) -> None:
        self.value = value
        if value:
            self.sketched_value = 0

    def set_sketched_value(self, value: int) -> None:
        self.sketched_value = value

    def draw(self, origin: Tuple[int, int]) -> None:
        x0 = origin[0] + self.col * self.size
        y0 = origin[1] + self.row * self.size
        rect = pygame.Rect(x0, y0, self.size, self.size)

        bg = LOCKED_BG if self.locked else WHITE
        pygame.draw.rect(self.screen, bg, rect)

        if self.selected:
            pygame.draw.rect(self.screen, SELECTED, rect, 3)
        else:
            pygame.draw.rect(self.screen, (200, 200, 200), rect, 1)

        if self.value != 0:
            color = BLACK if self.locked else SLATE
            text = self.fonts.value_font.render(str(self.value), True, color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        elif self.sketched_value != 0:
            text = self.fonts.sketch_font.render(str(self.sketched_value), True, SKETCH_GRAY)
            self.screen.blit(text, (x0 + 6, y0 + 4))
