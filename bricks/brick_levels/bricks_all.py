
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import sys
import random
import math
import json
import os

# --- Constants ---
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Game element constants
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 6
FAST_PADDLE_SPEED = 12

BALL_SIZE = 12
BALL_SPEED = 5

BRICK_ROWS = 5
BRICK_COLS = 8
BRICK_WIDTH = 80
BRICK_HEIGHT = 25
BRICK_GAP = 2

STARTING_LIVES = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (200, 0, 0)
BLUE = (0, 100, 200)

# Brick color definitions
BRICK_COLORS = {
    1: (0, 100, 200),     # Blue (1 hit)
    2: (200, 0, 0),       # Red (2 hits)
    3: (0, 200, 0),       # Green (3 hits)
    4: (255, 255, 0),     # Yellow (4 hits)
    5: (255, 165, 0),     # Orange (5 hits)
    6: (128, 128, 128)    # Gray (Unbreakable)
}

def get_brick_color(color_level):
    return BRICK_COLORS.get(color_level, (255, 255, 255))

# ...existing classes (Paddle, Ball, Brick, LevelManager)...

def show_modal(screen, font, prev_stats=None):
    """Display modal with level selection and game mode buttons"""
    modal_rect = pygame.Rect(100, 200, 800, 300)
    
    # Define level button dimensions and spacing
    level_btn_width, level_btn_height = 150, 50  # Make buttons bigger
    spacing = 20
    
    # Scan for available levels
    levels_dir = "levels"
    level_buttons = []
    level_num = 1
    
    # Calculate starting X position to center the buttons
    while os.path.exists(os.path.join(levels_dir, f"level{level_num}.json")):
        level_buttons.append(level_num)
        level_num += 1
    
    total_width = (len(level_buttons) * level_btn_width) + ((len(level_buttons) - 1) * spacing)
    start_x = modal_rect.x + (modal_rect.width - total_width) // 2
    
    # Create button rectangles
    button_rects = []
    for i, level in enumerate(level_buttons):
        x = start_x + i * (level_btn_width + spacing)
        y = modal_rect.y + 50
        button_rects.append((pygame.Rect(x, y, level_btn_width, level_btn_height), level))
    
    selected_level = 1
    
    # Game mode buttons
    start_button = pygame.Rect(modal_rect.x + 50, modal_rect.y + 200, 200, 50)
    auto_button = pygame.Rect(modal_rect.x + 300, modal_rect.y + 200, 200, 50)
    fast_button = pygame.Rect(modal_rect.x + 550, modal_rect.y + 200, 200, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Check level button clicks
                for btn_rect, level in button_rects:
                    if btn_rect.collidepoint(event.pos):
                        selected_level = level
                        break
                # Check game mode button clicks
                if start_button.collidepoint(event.pos):
                    return "manual", selected_level
                elif auto_button.collidepoint(event.pos):
                    return "autoplay", selected_level
                elif fast_button.collidepoint(event.pos):
                    return "fast_autoplay", selected_level
        
        # Draw everything
        screen.fill(BLACK)
        pygame.draw.rect(screen, GRAY, modal_rect)
        
        # Draw title and instructions
        title = font.render("BRICK BREAKER", True, WHITE)
        select_text = font.render("Select Level:", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, modal_rect.y - 40))
        screen.blit(select_text, (modal_rect.x + 50, modal_rect.y + 20))
        
        # Draw level buttons with filled background for better visibility
        for btn_rect, level in button_rects:
            color = RED if level == selected_level else GRAY
            pygame.draw.rect(screen, color, btn_rect)
            pygame.draw.rect(screen, WHITE, btn_rect, 2)
            level_text = font.render(f"Level {level}", True, WHITE)
            text_rect = level_text.get_rect(center=btn_rect.center)
            screen.blit(level_text, text_rect)
        
        # Draw game mode buttons
        for btn, (text, color) in zip(
            [start_button, auto_button, fast_button],
            [("Start Game", BLACK), ("Autoplay", BLACK), ("Fast Autoplay", BLACK)]
        ):
            pygame.draw.rect(screen, WHITE, btn)
            btn_text = font.render(text, True, color)
            screen.blit(btn_text, btn_text.get_rect(center=btn.center))
        
        pygame.display.flip()

def calculate_intercept_position(ball_x, ball_y, ball_dx, ball_dy, target_x, target_y, paddle_y, try_alternative=False):
    """Calculate where to position paddle to hit ball toward target"""
    if ball_dy > 0:  # Ball is falling
        time_to_paddle = (paddle_y - ball_y) / ball_dy
        landing_x = ball_x + (ball_dx * time_to_paddle)
        
        if ball_dx > 0:
            landing_x -= PADDLE_WIDTH * 0.2
        else:
            landing_x += PADDLE_WIDTH * 0.2
            
        landing_x = max(PADDLE_WIDTH/2, min(WINDOW_WIDTH - PADDLE_WIDTH/2, landing_x))
        return landing_x

    time_to_paddle = (paddle_y - ball_y) / ball_dy if ball_dy != 0 else 0
    intersection_x = ball_x + (ball_dx * time_to_paddle)
    dx_to_target = target_x - intersection_x
    
    dy_to_target = target_y - ball_y
    angle_factor = 0.5
    if dy_to_target < -WINDOW_HEIGHT/3:
        angle_factor = 0.8
    
    offset = dx_to_target * angle_factor
    max_offset = PADDLE_WIDTH * 0.9
    offset = max(-max_offset, min(max_offset, offset))
    return intersection_x + offset

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Brick Breaker")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    prev_stats = None
    
    while True:
        mode, selected_level = show_modal(screen, font, prev_stats)
        
        game_completed = False
        level_manager = LevelManager()
        level_manager.current_level = selected_level
        
        # ...rest of the game loop implementation...

if __name__ == "__main__":
    main()
