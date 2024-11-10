# lib/config.py

import pygame

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 700  # Adjusted as per new layout

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 150, 150)
SELECTED_CELL_COLOR = (189, 214, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)  # Blue color for buttons

# Fonts
FONT = pygame.font.SysFont("comicsans", 60)  # For Victory message
BUTTON_FONT = pygame.font.SysFont("comicsans", 30)
NUMBER_FONT = pygame.font.SysFont("comicsans", 40)
STATUS_FONT = pygame.font.SysFont("comicsans", 30)

# UI Element Heights
BUTTON_BAR_HEIGHT = 50
STATUS_BAR_HEIGHT = 40
MENU_BAR_HEIGHT = 60
SPACING = 10  # Added spacing between menu and grid
TOP_OFFSET = BUTTON_BAR_HEIGHT + STATUS_BAR_HEIGHT + MENU_BAR_HEIGHT + SPACING
