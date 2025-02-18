import pygame

# Color definitions for different brick levels
BRICK_COLORS = {
    1: (0, 100, 200),     # Blue (1 hit)
    2: (200, 0, 0),       # Red (2 hits)
    3: (0, 200, 0),       # Green (3 hits)
    4: (255, 255, 0),     # Yellow (4 hits)
    5: (255, 165, 0),     # Orange (5 hits) - kept for compatibility
    6: (128, 128, 128)    # Gray (Unbreakable)
}

def get_brick_color(color_level):
    return BRICK_COLORS.get(color_level, (255, 255, 255))  # Default to white if color not found
