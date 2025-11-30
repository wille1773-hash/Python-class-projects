"""Main entry point for the Sudoku GUI application."""
from __future__ import annotations

import os
import sys
from typing import List, Optional

import pygame

from board import Board

WIDTH, HEIGHT = 800, 900
BG_COLOR = (245, 244, 240)
TEXT_COLOR = (23, 23, 23)
BUTTON_COLOR = (227, 176, 95)
BUTTON_HOVER = (244, 205, 143)
BUTTON_TEXT = (41, 30, 18)
BUTTON_BORDER = (42, 34, 26)
WELCOME_BG_PATH = "assets/welcome_bg.png"


class Button:
    def __init__(
        self,
        label: str,
        rect: pygame.Rect,
        value: Optional[str] = None,
        base_color: Optional[tuple[int, int, int]] = None,
        hover_color: Optional[tuple[int, int, int]] = None,
        text_color: Optional[tuple[int, int, int]] = None,
    ) -> None:
        self.label = label
        self.rect = rect
        self.value = value
        self.hovered = False
        self.base_color = base_color or BUTTON_COLOR
        self.hover_color = hover_color or BUTTON_HOVER
        self.text_color = text_color or BUTTON_TEXT

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(screen, BUTTON_BORDER, self.rect, border_radius=12)
        inner = self.rect.inflate(-6, -6)
        pygame.draw.rect(screen, color, inner, border_radius=10)
        text = font.render(self.label, True, self.text_color)
        text_rect = text.get_rect(center=inner.center)
        screen.blit(text, text_rect)

    def update_hover(self, mouse_pos) -> None:
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, pos) -> bool:
        return self.rect.collidepoint(pos)


def resolve_font(
    candidates: List[str],
    size: int,
    bold: bool = False,
    italic: bool = False,
) -> pygame.font.Font:
    for name in candidates:
        match = pygame.font.match_font(name, bold=bold, italic=italic)
        if match:
            return pygame.font.Font(match, size)
    return pygame.font.SysFont(None, size, bold=bold, italic=italic)


def load_start_background() -> Optional[pygame.Surface]:
    if not os.path.exists(WELCOME_BG_PATH):
        return None
    image = pygame.image.load(WELCOME_BG_PATH).convert()
    return pygame.transform.scale(image, (WIDTH, HEIGHT))


def create_start_buttons() -> List[Button]:
    buttons = []
    labels = [("Easy", "easy"), ("Medium", "medium"), ("Hard", "hard")]
    start_y = 360
    for idx, (label, value) in enumerate(labels):
        rect = pygame.Rect(WIDTH // 2 - 120, start_y + idx * 90, 240, 62)
        buttons.append(
            Button(
                label,
                rect,
                value,
                base_color=(249, 232, 200),
                hover_color=(255, 241, 210),
                text_color=(52, 45, 36),
            )
        )
    return buttons


def create_control_buttons() -> List[Button]:
    labels = ["Reset", "Restart", "Exit"]
    buttons = []
    spacing = 160
    start_x = WIDTH // 2 - spacing
    y = HEIGHT - 110
    for idx, label in enumerate(labels):
        rect = pygame.Rect(start_x + idx * spacing, y, 120, 50)
        buttons.append(Button(label, rect, label.lower()))
    return buttons


def create_end_buttons() -> List[Button]:
    play_again = Button("Play Again", pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2, 150, 55), "restart")
    exit_button = Button("Exit", pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2, 130, 55), "exit")
    return [play_again, exit_button]


def draw_start_screen(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    subtitle_font: pygame.font.Font,
    button_font: pygame.font.Font,
    buttons: List[Button],
    background: Optional[pygame.Surface],
) -> None:
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill(BG_COLOR)

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    screen.blit(overlay, (0, 0))

    title = title_font.render("Welcome to Sudoku", True, (255, 251, 240))
    subtitle = subtitle_font.render("Please choose your difficulty", True, (255, 240, 212))

    title_rect = title.get_rect(center=(WIDTH // 2, 200))
    title_shadow = title_font.render("Welcome to Sudoku", True, (0, 0, 0))
    title_shadow_rect = title_shadow.get_rect(center=(WIDTH // 2 + 4, 204))
    screen.blit(title_shadow, title_shadow_rect)
    screen.blit(title, title_rect)

    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 270))
    subtitle_shadow = subtitle_font.render("Please choose your difficulty", True, (0, 0, 0))
    subtitle_shadow_rect = subtitle_shadow.get_rect(center=(WIDTH // 2 + 2, 272))
    screen.blit(subtitle_shadow, subtitle_shadow_rect)
    screen.blit(subtitle, subtitle_rect)

    for button in buttons:
        button.draw(screen, button_font)


def draw_game_screen(
    screen: pygame.Surface,
    board: Board,
    button_font: pygame.font.Font,
    control_buttons: List[Button],
    status_font: pygame.font.Font,
    difficulty: str,
    message: str = "",
) -> None:
    screen.fill(BG_COLOR)
    board.draw()
    difficulty_text = status_font.render(f"Difficulty: {difficulty.title()}", True, TEXT_COLOR)
    screen.blit(difficulty_text, (40, 30))
    helper = "Click a cell, type 1-9 to sketch, Enter to place, Backspace to clear."
    helper_text = status_font.render(helper, True, TEXT_COLOR)
    screen.blit(helper_text, (40, HEIGHT - 160))

    if message:
        msg_text = status_font.render(message, True, (180, 40, 40))
        screen.blit(msg_text, (40, HEIGHT - 190))

    for button in control_buttons:
        button.draw(screen, button_font)


def draw_end_screen(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    subtitle_font: pygame.font.Font,
    button_font: pygame.font.Font,
    buttons: List[Button],
    won: bool,
) -> None:
    screen.fill(BG_COLOR)
    title = "You solved it!" if won else "Sudoku Incorrect"
    subtitle = "Great job completing the puzzle." if won else "Something's off — try again."
    title_text = title_font.render(title, True, TEXT_COLOR)
    subtitle_text = subtitle_font.render(subtitle, True, TEXT_COLOR)
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 90)))
    screen.blit(subtitle_text, subtitle_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
    for button in buttons:
        button.draw(screen, button_font)


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")
    clock = pygame.time.Clock()

    start_background = load_start_background()

    title_font = resolve_font(["cooperblack", "papyrus", "futura"], 70, bold=True)
    subtitle_font = resolve_font(["noteworthy", "marker felt", "gill sans"], 30, italic=True)
    button_font = resolve_font(["avenir next", "gill sans", "arial"], 28, bold=True)
    status_font = resolve_font(["avenir next", "gill sans", "arial"], 22)

    start_buttons = create_start_buttons()
    control_buttons = create_control_buttons()
    end_buttons = create_end_buttons()

    state = "start"
    board: Optional[Board] = None
    difficulty = ""
    message = ""

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        if state == "start":
            for button in start_buttons:
                button.update_hover(mouse_pos)
        elif state == "playing":
            for button in control_buttons:
                button.update_hover(mouse_pos)
        elif state in ("win", "lose"):
            for button in end_buttons:
                button.update_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if state == "start":
                    for button in start_buttons:
                        if button.is_clicked(event.pos):
                            difficulty = button.value or "easy"
                            board = Board(WIDTH, HEIGHT, screen, difficulty)
                            state = "playing"
                            message = ""
                            break
                elif state == "playing" and board:
                    clicked_button = next((b for b in control_buttons if b.is_clicked(event.pos)), None)
                    if clicked_button:
                        if clicked_button.value == "reset":
                            board.reset_to_original()
                            message = "Board reset to initial puzzle."
                        elif clicked_button.value == "restart":
                            board = None
                            state = "start"
                        elif clicked_button.value == "exit":
                            running = False
                    else:
                        cell_pos = board.click(*event.pos)
                        if cell_pos:
                            row, col = cell_pos
                            board.select(row, col)
                elif state in ("win", "lose"):
                    for button in end_buttons:
                        if button.is_clicked(event.pos):
                            if button.value == "restart":
                                board = None
                                state = "start"
                            elif button.value == "exit":
                                running = False
                            break
            elif event.type == pygame.KEYDOWN and state == "playing" and board:
                if event.key == pygame.K_ESCAPE:
                    board = None
                    state = "start"
                elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE, pygame.K_0):
                    board.clear()
                elif event.key == pygame.K_RETURN:
                    board.commit_sketched_value()
                    if board.is_full():
                        state = "win" if board.check_board() else "lose"
                elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                    moves = {
                        pygame.K_UP: (-1, 0),
                        pygame.K_DOWN: (1, 0),
                        pygame.K_LEFT: (0, -1),
                        pygame.K_RIGHT: (0, 1),
                    }
                    d_row, d_col = moves[event.key]
                    board.move_selection(d_row, d_col)
                else:
                    if event.unicode.isdigit():
                        value = int(event.unicode)
                        if 1 <= value <= 9:
                            board.sketch(value)

        if state == "start":
            draw_start_screen(
                screen,
                title_font,
                subtitle_font,
                button_font,
                start_buttons,
                start_background,
            )
        elif state == "playing" and board:
            draw_game_screen(screen, board, button_font, control_buttons, status_font, difficulty, message)
        elif state == "win":
            draw_end_screen(screen, title_font, subtitle_font, button_font, end_buttons, True)
        elif state == "lose":
            draw_end_screen(screen, title_font, subtitle_font, button_font, end_buttons, False)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
