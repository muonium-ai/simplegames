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
)

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

def redraw_window(win, grid, selected_num, elapsed_time, message, game_over):
    win.fill(WHITE)
    draw_menu(win, selected_num)
    grid.draw(win)
    filled_cells = grid.count_filled()
    draw_status_bar(win, elapsed_time, message, filled_cells)

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
