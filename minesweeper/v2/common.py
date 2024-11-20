import pygame
from enum import Enum
from config import *

class CellState(Enum):
    HIDDEN = 0
    REVEALED = 1
    FLAGGED = 2

class Button:
    def __init__(self, x, y, text, height=30):
        self.text = text
        self.height = height
        self.is_hovered = False
        
        # Calculate width based on text
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, WHITE)
        self.width = max(text_surface.get_width() + 20, 110)  # Min width 110px
        
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def handle_event(self, event):
        """Handle mouse events for the button"""
        mouse_pos = pygame.mouse.get_pos()
        
        # Update hover state
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Handle click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:  # Left click
                return True
        return False

    def draw(self, screen, font):
        color = BUTTON_HOVER_COLOR if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update_text(self, text):
        self.text = text
    
    def set_paused(self, paused):
        self.paused = paused
        self.color = PAUSE_COLOR if paused else BUTTON_COLOR

class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = BLACK
        self.text = text
        self.txt_surface = pygame.font.Font(None, 32).render(text, True, WHITE)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = pygame.font.Font(None, 32).render(self.text, True, WHITE)
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_mine = False
        self.state = CellState.HIDDEN
        self.neighbor_mines = 0
        self.was_clicked = False
        self.is_flagged_in_game = False  # Add this line
        self.number = 0
