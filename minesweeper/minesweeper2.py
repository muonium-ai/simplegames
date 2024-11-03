# minesweeper2.py

import pygame
import random
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import os

# Configuration
class Config:
    CELL_SIZE = 32
    GRID_WIDTH = 30
    GRID_HEIGHT = 16
    MINE_COUNT = 99
    HEADER_HEIGHT = 70
    PADDING = 10
    MAX_HINTS = 5
    
    WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
    WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + HEADER_HEIGHT
    
    COLORS = {
        # Base colors
        'GRAY': (192, 192, 192),
        'DARK_GRAY': (128, 128, 128),
        'WHITE': (255, 255, 255),
        'BLACK': (0, 0, 0),
        'RED': (255, 0, 0),
        
        # UI colors
        'BUTTON': (70, 130, 180),        # Steel Blue
        'BUTTON_HOVER': (100, 149, 237),  # Cornflower Blue
        'BUTTON_DISABLED': (160, 160, 160),
        
        # Game state colors
        'DARK_GREEN': (0, 128, 0),
        'DARK_RED': (128, 0, 0),
        'DARK_BLUE': (0, 0, 128),
        'BROWN': (128, 128, 0),
        
        # Status colors
        'VICTORY': (0, 128, 0),    # Dark Green
        'DEFEAT': (255, 0, 0),     # Red
        'PAUSE': (128, 128, 0),    # Brown
        
        # Cell colors
        'REVEALED': (192, 192, 192),
        'HIDDEN': (128, 128, 128),
        'FLAG': (255, 0, 0),
        'MINE': (0, 0, 0),
    }
    
    NUMBER_COLORS = {
        1: (0, 0, 255),      # Blue
        2: (0, 128, 0),      # Green
        3: (255, 0, 0),      # Red
        4: (0, 0, 128),      # Dark Blue
        5: (128, 0, 0),      # Dark Red
        6: (0, 128, 128),    # Teal
        7: (0, 0, 0),        # Black
        8: (128, 128, 128),  # Gray
    }

class GameState(Enum):
    READY = auto()
    PLAYING = auto()
    PAUSED = auto()
    WON = auto()
    LOST = auto()

class CellState(Enum):
    HIDDEN = auto()
    REVEALED = auto()
    FLAGGED = auto()

@dataclass
class Cell:
    is_mine: bool = False
    state: CellState = CellState.HIDDEN
    neighbor_mines: int = 0

class Grid:
    def __init__(self, width: int, height: int, mine_count: int):
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.cells = [[Cell() for _ in range(width)] for _ in range(height)]
        self.first_click = True
    
    def place_mines(self, first_x: int, first_y: int) -> None:
        safe_cells = [(first_x, first_y)]
        safe_cells.extend([
            (first_x + dx, first_y + dy)
            for dx in [-1, 0, 1] for dy in [-1, 0, 1]
            if 0 <= first_x + dx < self.width and 0 <= first_y + dy < self.height
        ])
        
        all_positions = [
            (x, y) for x in range(self.width) for y in range(self.height)
            if (x, y) not in safe_cells
        ]
        
        mine_positions = random.sample(all_positions, self.mine_count)
        for x, y in mine_positions:
            self.cells[y][x].is_mine = True
        
        self._calculate_neighbors()
    
    def _calculate_neighbors(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if not self.cells[y][x].is_mine:
                    self.cells[y][x].neighbor_mines = self._count_adjacent_mines(x, y)
    
    def _count_adjacent_mines(self, x: int, y: int) -> int:
        return sum(
            self.cells[y + dy][x + dx].is_mine
            for dx in [-1, 0, 1] for dy in [-1, 0, 1]
            if 0 <= x + dx < self.width and 0 <= y + dy < self.height
            and (dx != 0 or dy != 0)
        )

class GameTimer:
    def __init__(self):
        self.start_time = 0
        self.pause_start = 0
        self.total_pause_time = 0
        self.is_paused = False
    
    def start(self):
        self.start_time = pygame.time.get_ticks()
        self.total_pause_time = 0
        self.is_paused = False
    
    def toggle_pause(self):
        current_time = pygame.time.get_ticks()
        if not self.is_paused:
            self.pause_start = current_time
            self.is_paused = True
        else:
            self.total_pause_time += current_time - self.pause_start
            self.is_paused = False
    
    def get_time(self) -> int:
        if self.is_paused:
            return (self.pause_start - self.start_time - self.total_pause_time) // 1000
        return (pygame.time.get_ticks() - self.start_time - self.total_pause_time) // 1000

class UIComponent:
    def draw(self, screen: pygame.Surface) -> None:
        raise NotImplementedError
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        raise NotImplementedError

class Button(UIComponent):
    def __init__(self, rect: pygame.Rect, text: str):
        self.rect = rect
        self.text = text
        self.is_hovered = False
        self._font = pygame.font.Font(None, 36)
    
    def draw(self, screen: pygame.Surface) -> None:
        color = Config.COLORS['BUTTON_HOVER'] if self.is_hovered else Config.COLORS['BUTTON']
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        
        text_surface = self._font.render(self.text, True, Config.COLORS['WHITE'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class InputBox(UIComponent):
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font):
        self.rect = rect
        self.text = text
        self.font = font
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.colors = {
            'inactive_border': Config.COLORS['WHITE'],
            'active_border': Config.COLORS['RED'],
            'background': Config.COLORS['DARK_GRAY'],
            'text': Config.COLORS['WHITE']
        }
        self._render_text()

    def _render_text(self):
        """Create text surface with current text"""
        self.txt_surface = self.font.render(self.text, True, self.colors['text'])

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events, return True if input changed"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on click
            self.active = self.rect.collidepoint(event.pos)
            return False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isdigit() and len(self.text) < 6:
                self.text += event.unicode
            else:
                return False
            self._render_text()
            return True
        return False

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the input box and text"""
        # Draw background
        pygame.draw.rect(screen, self.colors['background'], self.rect)
        
        # Draw border with active/inactive color
        border_color = self.colors['active_border'] if self.active else self.colors['inactive_border']
        pygame.draw.rect(screen, border_color, self.rect, 2)
        
        # Draw text
        text_pos = (self.rect.x + 5, self.rect.y + (self.rect.height - self.txt_surface.get_height()) // 2)
        screen.blit(self.txt_surface, text_pos)
        
        # Draw cursor if active
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer % 60 < 30:  # Blink every 30 frames
                cursor_pos = text_pos[0] + self.txt_surface.get_width() + 2
                pygame.draw.line(screen, 
                               self.colors['text'],
                               (cursor_pos, self.rect.y + 5),
                               (cursor_pos, self.rect.y + self.rect.height - 5))

    def get_value(self) -> int:
        """Get the numeric value of the input"""
        try:
            return int(self.text)
        except ValueError:
            return 0

class Minesweeper:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption("Minesweeper")
        
        # Game state
        self.grid = Grid(Config.GRID_WIDTH, Config.GRID_HEIGHT, Config.MINE_COUNT)
        self.timer = GameTimer()
        self.state = GameState.READY
        self.hints_used = 0
        self.quick_start_used = False
        self.seed = random.randint(1, 999999)
        
        # Initialize UI and resources
        self._init_ui()
        self._load_resources()

    def _new_game(self) -> None:
        self.seed = random.randint(1, 999999)
        self.grid = Grid(Config.GRID_WIDTH, Config.GRID_HEIGHT, Config.MINE_COUNT)
        self.state = GameState.READY
        self.hints_used = 0
        self.timer.start()

    def _restart_game(self) -> None:
        random.seed(self.seed)
        self.grid = Grid(Config.GRID_WIDTH, Config.GRID_HEIGHT, Config.MINE_COUNT)
        self.state = GameState.READY
        self.hints_used = 0
        self.timer.start()

    def _quick_start(self) -> None:
        """Handle quick start - can only be used once"""
        if self.quick_start_used:
            return
            
        self._new_game()
        self.state = GameState.PLAYING
        self.grid.first_click = False
        self.grid.place_mines(0, 0)
        
        # Reveal 5 random safe cells
        safe_cells = [
            (x, y) 
            for x in range(Config.GRID_WIDTH) 
            for y in range(Config.GRID_HEIGHT) 
            if not self.grid.cells[y][x].is_mine
        ]
        for x, y in random.sample(safe_cells, min(5, len(safe_cells))):
            self._reveal_cell(x, y)
        
        self.quick_start_used = True
        self.hints_used = 0  # Reset hints for new game

    def _hint(self) -> None:
        """Provide hint by revealing a safe cell"""
        if (self.state != GameState.PLAYING or 
            self.hints_used >= Config.MAX_HINTS):
            return
            
        safe_cells = [
            (x, y) 
            for x in range(Config.GRID_WIDTH) 
            for y in range(Config.GRID_HEIGHT)
            if not self.grid.cells[y][x].is_mine 
            and self.grid.cells[y][x].state == CellState.HIDDEN
        ]
        
        if safe_cells:
            x, y = random.choice(safe_cells)
            self._reveal_cell(x, y)
            self.hints_used += 1

    def _solve(self) -> None:
        if self.state != GameState.PLAYING:
            return
            
        for y in range(Config.GRID_HEIGHT):
            for x in range(Config.GRID_WIDTH):
                cell = self.grid.cells[y][x]
                if cell.is_mine:
                    if cell.state != CellState.FLAGGED:
                        cell.state = CellState.FLAGGED
                elif cell.state == CellState.HIDDEN:
                    cell.state = CellState.REVEALED
        
        self.state = GameState.WON

    def _toggle_pause(self) -> None:
        if self.state not in [GameState.PLAYING, GameState.PAUSED]:
            return
            
        self.state = GameState.PAUSED if self.state == GameState.PLAYING else GameState.PLAYING
        self.timer.toggle_pause()

    def _reveal_cell(self, x: int, y: int) -> None:
        if self.state not in [GameState.READY, GameState.PLAYING]:
            return
            
        cell = self.grid.cells[y][x]
        if cell.state != CellState.HIDDEN:
            return
            
        if self.state == GameState.READY:
            self.state = GameState.PLAYING
            self.timer.start()
            if self.grid.first_click:
                self.grid.place_mines(x, y)
                self.grid.first_click = False
        
        cell.state = CellState.REVEALED
        
        if cell.is_mine:
            self.state = GameState.LOST
            return
            
        if cell.neighbor_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < Config.GRID_WIDTH and 
                        0 <= ny < Config.GRID_HEIGHT):
                        self._reveal_cell(nx, ny)

    def _toggle_flag(self, x: int, y: int) -> None:
        if self.state != GameState.PLAYING:
            return
            
        cell = self.grid.cells[y][x]
        if cell.state == CellState.REVEALED:
            return
            
        cell.state = (
            CellState.HIDDEN 
            if cell.state == CellState.FLAGGED 
            else CellState.FLAGGED
        )

    def _check_victory(self) -> None:
        if self.state != GameState.PLAYING:
            return
            
        for y in range(Config.GRID_HEIGHT):
            for x in range(Config.GRID_WIDTH):
                cell = self.grid.cells[y][x]
                if not cell.is_mine and cell.state != CellState.REVEALED:
                    return
                    
        self.state = GameState.WON

    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        while running:
            running = self._handle_events()
            self._update()
            self._draw()
            clock.tick(60)
        
        pygame.quit()

    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            self._handle_game_event(event)
        
        return True

    def _handle_game_event(self, event: pygame.event.Event) -> None:
        # Handle button clicks
        for name, button in self.buttons.items():
            if button.handle_event(event):
                self._handle_button_click(name)
                return
        
        # Handle grid clicks
        if event.type == pygame.MOUSEBUTTONDOWN and self.state == GameState.PLAYING:
            self._handle_grid_click(event)

    def _handle_button_click(self, button_name: str) -> None:
        actions = {
            'new_game': self._new_game,
            'restart': self._restart_game,
            'quick_start': self._quick_start,
            'hint': self._hint,
            'solve': self._solve,
            'pause': self._toggle_pause
        }
        if action := actions.get(button_name):
            action()

    def _handle_grid_click(self, event: pygame.event.Event) -> None:
        x = event.pos[0] // Config.CELL_SIZE
        y = (event.pos[1] - Config.HEADER_HEIGHT) // Config.CELL_SIZE
        
        if not (0 <= x < Config.GRID_WIDTH and 0 <= y < Config.GRID_HEIGHT):
            return
        
        if event.button == 1:  # Left click
            self._reveal_cell(x, y)
        elif event.button == 3:  # Right click
            self._toggle_flag(x, y)

    def _update(self) -> None:
        if self.state == GameState.PLAYING:
            self._check_victory()

    def _draw(self) -> None:
        self.screen.fill(Config.COLORS['GRAY'])
        self._draw_header()
        self._draw_grid()
        pygame.display.flip()

    def _init_ui(self):
        """Initialize UI components and layout"""
        # First row - Buttons
        button_y = 10  # Top row
        current_x = Config.PADDING
        button_height = 30
        
        button_configs = [
            ("new_game", 100),
            ("restart", 100),
            ("quick_start", 120),
            ("hint", 80),
            ("pause", 80)
        ]
        
        self.buttons = {}
        for name, width in button_configs:
            self.buttons[name] = Button(
                pygame.Rect(current_x, button_y, width, button_height),
                name.replace('_', ' ').title()
            )
            current_x += width + Config.PADDING

        # Second row - Statistics
        stats_y = button_y + button_height + 10  # Second row
        self.stats_positions = {
            'time': (Config.PADDING, stats_y),
            'mines': (Config.WINDOW_WIDTH // 3, stats_y),
            'hints': (2 * Config.WINDOW_WIDTH // 3, stats_y),
            'status': (Config.WINDOW_WIDTH // 2, stats_y)
        }

    def _draw_header(self) -> None:
        """Draw header with controls and statistics"""
        # Draw header background
        pygame.draw.rect(
            self.screen,
            Config.COLORS['DARK_GRAY'],
            (0, 0, Config.WINDOW_WIDTH, Config.HEADER_HEIGHT)
        )

        # Draw buttons
        for name, button in self.buttons.items():
            if name == 'quick_start' and self.quick_start_used:
                button.enabled = False
            elif name == 'hint' and self.hints_used >= Config.MAX_HINTS:
                button.enabled = False
            button.draw(self.screen)

        # Draw statistics in second row
        font = pygame.font.Font(None, 32)
        
        # Time
        time_text = f"Time: {self.timer.get_time()}s"
        self._draw_text(time_text, pygame.Rect(*self.stats_positions['time'], 0, 0), Config.COLORS['BLACK'])
        
        # Mines
        mines_text = f"Mines: {self.grid.mine_count}"
        self._draw_text(mines_text, pygame.Rect(*self.stats_positions['mines'], 0, 0), Config.COLORS['RED'])
        
        # Hints
        hints_text = f"Hints: {self.hints_used}/{Config.MAX_HINTS}"
        self._draw_text(hints_text, pygame.Rect(*self.stats_positions['hints'], 0, 0), Config.COLORS['BLACK'])
        
        # Game status
        if self.state in [GameState.WON, GameState.LOST, GameState.PAUSED]:
            status_texts = {
                GameState.WON: "Victory!",
                GameState.LOST: "Game Over!",
                GameState.PAUSED: "Paused"
            }
            status_colors = {
                GameState.WON: Config.COLORS['VICTORY'],
                GameState.LOST: Config.COLORS['DEFEAT'],
                GameState.PAUSED: Config.COLORS['PAUSE']
            }
            self._draw_text(
                status_texts[self.state],
                pygame.Rect(*self.stats_positions['status'], 0, 0),
                status_colors[self.state]
            )

    def _draw_grid(self) -> None:
        for y in range(Config.GRID_HEIGHT):
            for x in range(Config.GRID_WIDTH):
                self._draw_cell(x, y)

    def _draw_cell(self, x: int, y: int) -> None:
        cell = self.grid.cells[y][x]
        rect = pygame.Rect(
            x * Config.CELL_SIZE,
            y * Config.CELL_SIZE + Config.HEADER_HEIGHT,
            Config.CELL_SIZE,
            Config.CELL_SIZE
        )
        
        # Draw cell background
        color = (
            Config.COLORS['GRAY']
            if cell.state == CellState.REVEALED
            else Config.COLORS['DARK_GRAY']
        )
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, Config.COLORS['WHITE'], rect, 1)
        
        # Draw cell content
        if cell.state == CellState.FLAGGED:
            if self.images_loaded:
                self._draw_image('flag', rect)
            else:
                self._draw_text('🚩', rect, Config.COLORS['RED'])
        elif cell.state == CellState.REVEALED:
            if cell.is_mine:
                if self.images_loaded:
                    self._draw_image('mine', rect)
                else:
                    self._draw_text('💣', rect, Config.COLORS['BLACK'])
            elif cell.neighbor_mines > 0:
                self._draw_text(
                    str(cell.neighbor_mines),
                    rect,
                    Config.NUMBER_COLORS[cell.neighbor_mines]
                )

    def _draw_image(self, image_name: str, rect: pygame.Rect) -> None:
        image = self.images[image_name]
        image_rect = image.get_rect(center=rect.center)
        self.screen.blit(image, image_rect)

    def _draw_text(self, text: str, rect: pygame.Rect, color: Tuple[int, int, int]) -> None:
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def _load_resources(self) -> None:
        """Load and prepare game resources like images"""
        self.images = {}
        self.images_loaded = False
        
        try:
            # Define image paths relative to script location
            base_path = os.path.dirname(os.path.abspath(__file__))
            image_paths = {
                'mine': os.path.join(base_path, 'images', 'landmine.png'),
                'flag': os.path.join(base_path, 'images', 'red-flag.png')
            }
            
            # Calculate scaled size (80% of cell size)
            scaled_size = int(Config.CELL_SIZE * 0.8)
            
            # Load and scale each image
            for name, path in image_paths.items():
                # Load image with alpha channel
                image = pygame.image.load(path).convert_alpha()
                # Scale to fit cell
                self.images[name] = pygame.transform.scale(
                    image,
                    (scaled_size, scaled_size)
                )
            
            self.images_loaded = True
            print("Resources loaded successfully")
            
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading resources: {e}")
            self.images_loaded = False
            self.images = {}  # Reset images dictionary

if __name__ == "__main__":
    game = Minesweeper()
    game.run()