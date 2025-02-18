import pygame

# Color definitions for different brick levels
BRICK_COLORS = {
    1: (135, 206, 235),  # Light Blue (1 hit)
    2: (0, 100, 200),    # Medium Blue (2 hits)
    3: (255, 165, 0),    # Orange (3 hits)
    4: (255, 0, 0),      # Red (4 hits)
    5: (128, 0, 128),    # Purple (5 hits)
    6: (169, 169, 169)   # Gray (Unbreakable)
}

def get_brick_color(color_level):
    return BRICK_COLORS.get(color_level, (255, 255, 255))  # Default to white if color not found
