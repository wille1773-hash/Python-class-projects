"""
Sudoku generator for the COP3502 final project.

The generator is responsible for creating a solved Sudoku grid, removing a
prescribed number of cells to create a playable puzzle, and exposing helpers that
the GUI can use to verify player moves.
"""
from __future__ import annotations

import random
from typing import List, Optional


class SudokuGenerator:
    """Backtracking Sudoku generator with helper query utilities."""

    def __init__(self, row_length: int, removed_cells: int) -> None:
        self.row_length = row_length
        self.removed_cells = removed_cells
        self.box_length = int(self.row_length ** 0.5)
        self.board: List[List[int]] = [
            [0 for _ in range(self.row_length)] for _ in range(self.row_length)
        ]
        self.solution: Optional[List[List[int]]] = None

    def get_board(self) -> List[List[int]]:
        return self.board

    def get_solution(self) -> List[List[int]]:
        if self.solution is None:
            raise ValueError("Solution requested before board was generated.")
        return self.solution

    def print_board(self) -> None:
        for row in self.board:
            print(" ".join(str(val) for val in row))

    def valid_in_row(self, row: int, num: int) -> bool:
        return num not in self.board[row]

    def valid_in_col(self, col: int, num: int) -> bool:
        return all(self.board[r][col] != num for r in range(self.row_length))

    def valid_in_box(self, row_start: int, col_start: int, num: int) -> bool:
        for r in range(self.box_length):
            for c in range(self.box_length):
                if self.board[row_start + r][col_start + c] == num:
                    return False
        return True

    def is_valid(self, row: int, col: int, num: int) -> bool:
        """Check whether placing num at (row, col) is legal."""
        return (
            self.valid_in_row(row, num)
            and self.valid_in_col(col, num)
            and self.valid_in_box(row - row % self.box_length, col - col % self.box_length, num)
        )

    def _unused_in_box(self, row_start: int, col_start: int) -> List[int]:
        used = {
            self.board[row_start + r][col_start + c]
            for r in range(self.box_length)
            for c in range(self.box_length)
            if self.board[row_start + r][col_start + c] != 0
        }
        return [num for num in range(1, self.row_length + 1) if num not in used]

    def fill_box(self, row_start: int, col_start: int) -> None:
        values = self._unused_in_box(row_start, col_start)
        random.shuffle(values)
        idx = 0
        for r in range(self.box_length):
            for c in range(self.box_length):
                if self.board[row_start + r][col_start + c] == 0:
                    self.board[row_start + r][col_start + c] = values[idx]
                    idx += 1

    def fill_diagonal(self) -> None:
        for start in range(0, self.row_length, self.box_length):
            self.fill_box(start, start)

    def fill_remaining(self, row: int = 0, col: int = 0) -> bool:
        if col >= self.row_length and row < self.row_length - 1:
            row += 1
            col = 0
        if row >= self.row_length and col >= self.row_length:
            return True

        if row < self.box_length:
            if col < self.box_length:
                col = self.box_length
        elif row < self.row_length - self.box_length:
            if col == (row // self.box_length) * self.box_length:
                col += self.box_length
        else:
            if col == self.row_length - self.box_length:
                row += 1
                col = 0
                if row >= self.row_length:
                    return True

        numbers = list(range(1, self.row_length + 1))
        random.shuffle(numbers)
        for num in numbers:
            if self.is_valid(row, col, num):
                self.board[row][col] = num
                if self.fill_remaining(row, col + 1):
                    return True
                self.board[row][col] = 0
        return False

    def fill_values(self) -> None:
        self.fill_diagonal()
        self.fill_remaining(0, self.box_length)
        self.solution = [row[:] for row in self.board]

    def remove_cells(self) -> None:
        removed = 0
        while removed < self.removed_cells:
            row = random.randrange(self.row_length)
            col = random.randrange(self.row_length)
            if self.board[row][col] != 0:
                self.board[row][col] = 0
                removed += 1


def generate_sudoku(size: int, removed: int) -> List[List[int]]:
    """Utility to create a Sudoku board with the requested number of blanks."""
    generator = SudokuGenerator(size, removed)
    generator.fill_values()
    generator.remove_cells()
    return generator.get_board()
