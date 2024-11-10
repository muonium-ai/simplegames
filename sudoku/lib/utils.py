# lib/utils.py

import pygame
from .config import (
    WIDTH,
    HEIGHT,
    RED,
    LIGHT_GRAY,
    BLACK,
    WHITE,
    NUMBER_FONT,
    STATUS_FONT,
    FONT,
    BUTTON_FONT,
    GREEN,
)
from .config import pygame  # Ensure pygame is initialized

def draw_menu(win, selected_num):
    gap = WIDTH / 9
    for i in range(9):
        x = i * gap
        y = 0
        rect = pygame.Rect(x, y, gap, 60)
        if selected_num == i + 1:
            pygame.draw.rect(win, LIGHT_GRAY, rect)
        pygame.draw.rect(win, BLACK, rect, 1)
        text = NUMBER_FONT.render(str(i + 1), True, RED)
        win.blit(
            text,
            (x + (gap / 2 - text.get_width() / 2), y + (60 / 2 - text.get_height() / 2)),
        )

def draw_status_bar(win, elapsed_time, message, filled_cells):
    status_bar_height = 40
    y = HEIGHT - status_bar_height
    pygame.draw.rect(win, LIGHT_GRAY, (0, y, WIDTH, status_bar_height))
    pygame.draw.line(win, BLACK, (0, y), (WIDTH, y), 2)

    time_text = STATUS_FONT.render(f"Time: {int(elapsed_time)}s", True, BLACK)
    cells_text = STATUS_FONT.render(f"Filled Cells: {filled_cells}/81", True, BLACK)
    message_text = STATUS_FONT.render(
        message, True, RED if message == "Invalid Move" else BLACK
    )

    win.blit(time_text, (10, y + 5))
    win.blit(cells_text, (200, y + 5))
    win.blit(message_text, (400, y + 5))

def draw_buttons(win):
    button_width = 150
    button_height = 40
    gap = 20
    y = HEIGHT - 100  # Position buttons above the status bar

    # New Game Button
    new_game_rect = pygame.Rect(
        (WIDTH / 2 - button_width / 2 - button_width - gap, y),
        (button_width, button_height),
    )
    pygame.draw.rect(win, LIGHT_GRAY, new_game_rect)
    pygame.draw.rect(win, BLACK, new_game_rect, 2)
    new_game_text = BUTTON_FONT.render("New Game", True, BLACK)
    win.blit(
        new_game_text,
        (
            new_game_rect.x + (button_width - new_game_text.get_width()) / 2,
            new_game_rect.y + (button_height - new_game_text.get_height()) / 2,
        ),
    )

    # Hint Button
    hint_rect = pygame.Rect(
        (WIDTH / 2 - button_width / 2, y), (button_width, button_height)
    )
    pygame.draw.rect(win, LIGHT_GRAY, hint_rect)
    pygame.draw.rect(win, BLACK, hint_rect, 2)
    hint_text = BUTTON_FONT.render("Hint", True, BLACK)
    win.blit(
        hint_text,
        (
            hint_rect.x + (button_width - hint_text.get_width()) / 2,
            hint_rect.y + (button_height - hint_text.get_height()) / 2,
        ),
    )

    # Solve Button
    solve_rect = pygame.Rect(
        (WIDTH / 2 + button_width / 2 + gap, y), (button_width, button_height)
    )
    pygame.draw.rect(win, LIGHT_GRAY, solve_rect)
    pygame.draw.rect(win, BLACK, solve_rect, 2)
    solve_text = BUTTON_FONT.render("Solve", True, BLACK)
    win.blit(
        solve_text,
        (
            solve_rect.x + (button_width - solve_text.get_width()) / 2,
            solve_rect.y + (button_height - solve_text.get_height()) / 2,
        ),
    )

    return {'new_game': new_game_rect, 'hint': hint_rect, 'solve': solve_rect}

def redraw_window(win, grid, selected_num, elapsed_time, message, game_over):
    win.fill(WHITE)
    draw_menu(win, selected_num)
    grid.draw(win)
    filled_cells = grid.count_filled()
    draw_status_bar(win, elapsed_time, message, filled_cells)
    buttons = draw_buttons(win)

    if game_over:
        # Display Victory message
        victory_text = FONT.render("Victory!", True, RED)
        win.blit(
            victory_text,
            (
                WIDTH / 2 - victory_text.get_width() / 2,
                HEIGHT / 2 - victory_text.get_height() / 2,
            ),
        )

    pygame.display.update()
    return buttons
