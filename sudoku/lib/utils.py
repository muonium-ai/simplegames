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
    BLUE,
    BUTTON_BAR_HEIGHT,
    STATUS_BAR_HEIGHT,
    MENU_BAR_HEIGHT,
    TOP_OFFSET,
    SPACING,
)
from .config import pygame  # Ensure pygame is initialized

def draw_menu(win, selected_num):
    gap = WIDTH / 9
    y = BUTTON_BAR_HEIGHT + STATUS_BAR_HEIGHT  # Adjusted position
    for i in range(9):
        x = i * gap
        rect = pygame.Rect(x, y, gap, MENU_BAR_HEIGHT)
        if selected_num == i + 1:
            pygame.draw.rect(win, LIGHT_GRAY, rect)
        pygame.draw.rect(win, BLACK, rect, 1)
        text = NUMBER_FONT.render(str(i + 1), True, RED)
        win.blit(
            text,
            (x + (gap / 2 - text.get_width() / 2), y + (MENU_BAR_HEIGHT / 2 - text.get_height() / 2)),
        )

def draw_status_bar(win, elapsed_time, message):
    y = BUTTON_BAR_HEIGHT  # Position below the buttons
    pygame.draw.rect(win, LIGHT_GRAY, (0, y, WIDTH, STATUS_BAR_HEIGHT))
    pygame.draw.line(win, BLACK, (0, y), (WIDTH, y), 2)

    time_text = STATUS_FONT.render(f"Time: {int(elapsed_time)}s", True, BLACK)
    message_text = STATUS_FONT.render(
        message, True, RED if message == "Invalid Move" else BLACK
    )

    win.blit(time_text, (10, y + 5))
    win.blit(message_text, (200, y +5))
    # Removed "Filled Cells" text to save space

def draw_buttons(win):
    button_width = 150
    button_height = 40
    gap = 20
    y = 0  # Position at the very top

    # New Game Button
    new_game_rect = pygame.Rect(
        (WIDTH / 2 - button_width / 2 - button_width - gap, y),
        (button_width, button_height),
    )
    pygame.draw.rect(win, LIGHT_GRAY, new_game_rect)
    pygame.draw.rect(win, BLACK, new_game_rect, 2)
    new_game_text = BUTTON_FONT.render("New Game", True, BLUE)  # Text in blue
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
    hint_text = BUTTON_FONT.render("Hint", True, BLUE)  # Text in blue
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
    solve_text = BUTTON_FONT.render("Solve", True, BLUE)  # Text in blue
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
    buttons = draw_buttons(win)
    draw_status_bar(win, elapsed_time, message)
    draw_menu(win, selected_num)
    grid.draw(win)
    
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
