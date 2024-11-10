# lib/config.py

import pygame

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 700  # Increased height for buttons

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
SELECTED_CELL_COLOR = (189, 214, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Fonts
FONT = pygame.font.SysFont("comicsans", 60)  # For Victory message
BUTTON_FONT = pygame.font.SysFont("comicsans", 30)
NUMBER_FONT = pygame.font.SysFont("comicsans", 40)
STATUS_FONT = pygame.font.SysFont("comicsans", 30)
