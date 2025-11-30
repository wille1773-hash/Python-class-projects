"""Sudoku board management and rendering."""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import pygame

from cell import Cell, FontBundle
from sudoku_generator import SudokuGenerator

DIFFICULTY_TO_REMOVED: Dict[str, int] = {
    "easy": 30,
    "medium": 40,
    "hard": 50,
}

GRID_MARGIN_TOP = 100
GRID_MARGIN_SIDE = 40
BACKGROUND = (250, 250, 250)
LINE_COLOR = (28, 28, 28)
THIN_LINE = (200, 200, 200)


class Board:
    """Encapsulates the Sudoku grid, state, and draw logic."""

    def __init__(
        self,
        width: int,
        height: int,
        screen: pygame.Surface,
        difficulty: str,
    ) -> None:
        self.width = width
        self.height = height
        self.screen = screen
        self.difficulty = difficulty.lower()
        removed = DIFFICULTY_TO_REMOVED.get(self.difficulty, 40)

        self.generator = SudokuGenerator(9, removed)
        self.generator.fill_values()
        self.solution = self.generator.get_solution()
        self.generator.remove_cells()
        board = self.generator.get_board()
        self.original_board = [row[:] for row in board]
        self.board = [row[:] for row in board]

        usable_width = max(360, self.width - 2 * GRID_MARGIN_SIDE)
        usable_height = max(360, self.height - GRID_MARGIN_TOP - 160)
        self.grid_pixels = min(540, min(usable_width, usable_height))
        self.cell_size = self.grid_pixels // 9
        self.origin = (
            (self.width - self.grid_pixels) // 2,
            GRID_MARGIN_TOP,
        )

        pygame.font.init()
        self.fonts = FontBundle(
            pygame.font.SysFont("arial", self.cell_size // 2 + 22),
            pygame.font.SysFont("arial", self.cell_size // 2),
        )

        self.cells: List[List[Cell]] = [
            [
                Cell(
                    board[r][c],
                    r,
                    c,
                    self.cell_size,
                    self.screen,
                    self.fonts,
                    locked=self.original_board[r][c] != 0,
                )
                for c in range(9)
            ]
            for r in range(9)
        ]
        self.selected: Optional[Tuple[int, int]] = None

    def draw(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.draw(self.origin)
        self._draw_grid_lines()

    def _draw_grid_lines(self) -> None:
        start_x, start_y = self.origin
        for i in range(10):
            width = 3 if i % 3 == 0 else 1
            color = LINE_COLOR if i % 3 == 0 else THIN_LINE
            pygame.draw.line(
                self.screen,
                color,
                (start_x, start_y + i * self.cell_size),
                (start_x + self.grid_pixels, start_y + i * self.cell_size),
                width,
            )
            pygame.draw.line(
                self.screen,
                color,
                (start_x + i * self.cell_size, start_y),
                (start_x + i * self.cell_size, start_y + self.grid_pixels),
                width,
            )

    def select(self, row: int, col: int) -> None:
        self._clear_selection()
        self.cells[row][col].selected = True
        self.selected = (row, col)

    def _clear_selection(self) -> None:
        for row in self.cells:
            for cell in row:
                cell.selected = False

    def click(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        start_x, start_y = self.origin
        if (
            start_x <= x <= start_x + self.grid_pixels
            and start_y <= y <= start_y + self.grid_pixels
        ):
            col = (x - start_x) // self.cell_size
            row = (y - start_y) // self.cell_size
            return int(row), int(col)
        return None

    def move_selection(self, d_row: int, d_col: int) -> None:
        if self.selected is None:
            self.select(0, 0)
            return
        row = max(0, min(8, self.selected[0] + d_row))
        col = max(0, min(8, self.selected[1] + d_col))
        self.select(row, col)

    def clear(self) -> None:
        if not self.selected:
            return
        row, col = self.selected
        cell = self.cells[row][col]
        if self.original_board[row][col] == 0:
            cell.set_cell_value(0)
            cell.set_sketched_value(0)
            self.board[row][col] = 0

    def sketch(self, value: int) -> None:
        if not self.selected:
            return
        row, col = self.selected
        if self.original_board[row][col] != 0:
            return
        self.cells[row][col].set_sketched_value(value)

    def place_number(self, value: int) -> None:
        if not self.selected:
            return
        row, col = self.selected
        if self.original_board[row][col] != 0:
            return
        self.cells[row][col].set_cell_value(value)
        self.board[row][col] = value

    def commit_sketched_value(self) -> None:
        if not self.selected:
            return
        row, col = self.selected
        if self.original_board[row][col] != 0:
            return
        sketch = self.cells[row][col].sketched_value
        if sketch != 0:
            self.place_number(sketch)

    def reset_to_original(self) -> None:
        for r in range(9):
            for c in range(9):
                self.cells[r][c].set_cell_value(self.original_board[r][c])
                self.cells[r][c].set_sketched_value(0)
                self.board[r][c] = self.original_board[r][c]
        self.selected = None
        self._clear_selection()

    def is_full(self) -> bool:
        return all(cell.value != 0 for row in self.cells for cell in row)

    def update_board(self) -> None:
        self.board = [[cell.value for cell in row] for row in self.cells]

    def find_empty(self) -> Optional[Tuple[int, int]]:
        for r in range(9):
            for c in range(9):
                if self.cells[r][c].value == 0:
                    return r, c
        return None

    def check_board(self) -> bool:
        self.update_board()
        for r in range(9):
            for c in range(9):
                if self.board[r][c] != self.solution[r][c]:
                    return False
        return True
