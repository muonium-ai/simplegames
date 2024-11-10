# lib/cell.py

import pygame
from .config import BLACK, GRAY, GREEN, SELECTED_CELL_COLOR, HIGHLIGHT_COLOR, NUMBER_FONT, TOP_OFFSET

class Cell:
    def __init__(self, value, row, col, width, height, editable):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.editable = editable
        self.selected = False
        self.highlighted = False
        self.hinted = False  # Attribute to track hinted or solved cells

    def draw(self, win):
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap + TOP_OFFSET  # Adjusted position

        if self.highlighted:
            pygame.draw.rect(win, HIGHLIGHT_COLOR, (x, y, gap, gap))

        if self.selected:
            pygame.draw.rect(win, SELECTED_CELL_COLOR, (x, y, gap, gap))

        if self.value != 0:
            if self.hinted:
                font_color = GREEN  # Hinted or solved numbers in green
            elif not self.editable:
                font_color = GRAY
            else:
                font_color = BLACK
            text = NUMBER_FONT.render(str(self.value), True, font_color)
            win.blit(
                text,
                (
                    x + (gap / 2 - text.get_width() / 2),
                    y + (gap / 2 - text.get_height() / 2),
                ),
            )
