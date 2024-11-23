from enum import Enum
import pygame
import random
from config import *
from common import Cell,CellState, Button, InputBox
import sys


class Minesweeper:
    # Add image paths as class constants
    FLAG_IMAGE_PATH = "images/red-flag.png"
    MINE_IMAGE_PATH = "images/landmine.png"

    def __init__(self, filename=None):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        #pygame.display.setCaption("Minesweeper")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 20)
        
        # Initialize game state # crash fixing
        self.total_moves = 0
        self.window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.window = pygame.display.set_mode(self.window_size)
        
        # Button layout with dynamic widths
        button_height = 30
        button_y = 10
        current_x = PADDING

        # Create buttons with dynamic positioning
        self.new_game_button = Button(current_x, button_y, "New Game")
        current_x += self.new_game_button.width + PADDING
        
        self.restart_button = Button(current_x, button_y, "Restart Game")
        current_x += self.restart_button.width + PADDING
        
        self.quick_start_button = Button(current_x, button_y, "Quick Start")
        current_x += self.quick_start_button.width + PADDING
        
        self.hint_button = Button(current_x, button_y, "Hint")
        current_x += self.hint_button.width + PADDING
        
        self.solve_button = Button(current_x, button_y, "Solve It")
        current_x += self.solve_button.width + PADDING

        self.pause_button = Button(current_x, button_y, "Pause")

        # Pause state
        self.is_paused = False
        self.pause_start_time = 0
        self.total_pause_time = 0
        self.points = 0
        self.clicks_made=0

        # Input box for seed and display for time, points, hints
        self.seed_input_box = InputBox(PADDING, HEADER_HEIGHT - 35, 100, 30)
        self.seed = None
        self.hints_used = 0

        # Add the debug_mode attribute
        self.debug_mode = False  # Set to True to enable debug messages

        self.left_clicks = 0
        self.right_clicks = 0
        self.both_clicks = 0
        self.clicks_made = 0

        # Load game configuration from file if provided
        if filename:
            self.load_game_from_file(filename)
        else:
            self.reset_game()

        # Load and scale images
        try:
            self.flag_img = pygame.image.load(self.FLAG_IMAGE_PATH).convert_alpha()
            self.mine_img = pygame.image.load(self.MINE_IMAGE_PATH).convert_alpha()
            
            # Calculate image size (80% of cell size)
            self.img_size = int(CELL_SIZE * 0.8)
            
            # Scale images
            self.flag_img = pygame.transform.scale(self.flag_img, 
                                                 (self.img_size, self.img_size))
            self.mine_img = pygame.transform.scale(self.mine_img, 
                                                 (self.img_size, self.img_size))
            
            self.images_loaded = True
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading images: {e}")
            self.images_loaded = False

    def load_game_from_file(self, filename):
        """Load game configuration from a file."""
        with open(filename, 'r') as file:
            lines = file.readlines()
        
        self.grid = [[Cell(x, y) for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
        self.game_over = False
        self.victory = False
        self.mines_remaining = 0
        self.unmarked_boxes = GRID_WIDTH * GRID_HEIGHT
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.first_click = True
        self.points = 0
        self.clicks_made = 0
        self.used_hint_or_quickplay = False
        self.hints_used = 0

        for y, line in enumerate(lines):
            for x, char in enumerate(line.strip()):
                cell = self.grid[y][x]
                if char == '*':
                    cell.is_mine = True
                    self.mines_remaining += 1
                elif char.isdigit():
                    cell.neighbor_mines = int(char)
                cell.state = CellState.HIDDEN  # Ensure all cells are hidden initially

        self.update_probabilities()

    def reset_game(self, seed=None):
        self.grid = [[Cell(x, y) for x in range(GRID_WIDTH)] for y in range(GRID_HEIGHT)]
        self.game_over = False
        self.victory = False
        self.mines_remaining = MINE_COUNT
        self.unmarked_boxes = GRID_WIDTH * GRID_HEIGHT
        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0
        self.first_click = True
        self.points = 0
        self.clicks_made=0
        self.used_hint_or_quickplay = False
        self.hints_used = 0  # Reset hint counter on new game
        if seed is None:
            self.seed = random.randint(0, 9999)
        else:
            self.seed = int(seed)
        random.seed(self.seed)
        self.seed_input_box.text = str(self.seed)
        self.seed_input_box.txt_surface = self.font.render(str(self.seed), True, WHITE)
        self.update_probabilities()

    def quick_start(self):
        if not self.first_click:
            return
        # track before state
        hidden_before = self.count_hidden()
        mines_remaining_before = self.mines_remaining
        
        self.used_hint_or_quickplay = True
        # Place mines but keep the existing seed
        self.first_click = False
        start_x = random.randint(0, GRID_WIDTH - 1)
        start_y = random.randint(0, GRID_HEIGHT - 1)
        self.place_mines(start_x, start_y)
        self.hints_used += 5
        
        # Find all safe cells and reveal 5 random ones
        safe_cells = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if not self.grid[y][x].is_mine]
        cells_to_reveal = random.sample(safe_cells, min(5, len(safe_cells)))
        for x, y in cells_to_reveal:
            self.reveal_cell(x, y)
            pos = (x * CELL_SIZE, y * CELL_SIZE + HEADER_HEIGHT)
            self.handle_click(pos)
            
        # Track after state 
        hidden_after = self.count_hidden()
        mines_remaining_after = self.mines_remaining

        if hidden_before != hidden_after or mines_remaining_before != mines_remaining_after:
            self.clicks_made += 5
        

    def hint(self):
        """Reveal a random safe cell as a hint"""
        # Find all safe hidden cells
        safe_hidden_cells = [
            (x, y) for y in range(GRID_HEIGHT) 
            for x in range(GRID_WIDTH)
            if not self.grid[y][x].is_mine 
            and self.grid[y][x].state == CellState.HIDDEN
        ]
        # track before state
        hidden_before = self.count_hidden()
        mines_remaining_before = self.mines_remaining
        
        if safe_hidden_cells:
            # Choose random safe cell
            x, y = random.choice(safe_hidden_cells)
            
            # Use reveal_cell instead of directly setting state
            self.reveal_cell(x, y)
            
            # Update hint tracking
            self.used_hint_or_quickplay = True
            self.hints_used += 1
            
            # Update probabilities after reveal
            #self.update_probabilities()
            #self.update_probabilities()
            pos = (x * CELL_SIZE, y * CELL_SIZE + HEADER_HEIGHT)
            self.handle_click(pos)
            
        # Track after state 
        hidden_after = self.count_hidden()
        mines_remaining_after = self.mines_remaining

        if hidden_before != hidden_after or mines_remaining_before != mines_remaining_after:
            self.clicks_made += 1
            
            # Check for victory
            self.check_victory()

    def solve_it(self):
        # Reveal all non-mine cells and flag all mines without changing the score
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell.is_mine:
                    cell.state = CellState.FLAGGED
                else:
                    cell.state = CellState.REVEALED
        # End the game and stop the timer
        self.game_over = True

    def place_mines(self, first_x, first_y):
        safe_cells = [(first_x, first_y)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    safe_cells.append((nx, ny))
        positions = [(x, y) for x in range(GRID_WIDTH) for y in range(GRID_HEIGHT) if (x, y) not in safe_cells]
        mine_positions = random.sample(positions, MINE_COUNT)
        for x, y in mine_positions:
            self.grid[y][x].is_mine = True
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if not self.grid[y][x].is_mine:
                    count = sum(1 for dx in [-1, 0, 1] for dy in [-1, 0, 1] 
                                if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT and self.grid[y + dy][x + dx].is_mine)
                    self.grid[y][x].neighbor_mines = count

    def reveal_cell(self, x, y):
        """Reveal a cell and calculate adjacent mines"""
        cell = self.grid[y][x]
        if cell.state != CellState.HIDDEN:
            return
            
        # Set cell as revealed
        cell.state = CellState.REVEALED
        
        # Calculate adjacent mines
        adjacent_mines = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < GRID_WIDTH and 
                    0 <= new_y < GRID_HEIGHT and 
                    self.grid[new_y][new_x].is_mine):
                    adjacent_mines += 1
        
        # Set number of adjacent mines
        cell.number = adjacent_mines
        
        # If no adjacent mines, reveal surrounding cells
        if adjacent_mines == 0:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    new_x, new_y = x + dx, y + dy
                    if (0 <= new_x < GRID_WIDTH and 
                        0 <= new_y < GRID_HEIGHT and 
                        self.grid[new_y][new_x].state == CellState.HIDDEN):
                        self.reveal_cell(new_x, new_y)

    def reveal_adjacent_cells(self, x, y):
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if (dx != 0 or dy != 0) and (0 <= nx < GRID_WIDTH) and (0 <= ny < GRID_HEIGHT):
                    self.reveal_cell(nx, ny)

    def handle_click(self, pos, right_click=False):
        if self.game_over or self.victory:
            return
        x = pos[0] // CELL_SIZE
        y = (pos[1] - HEADER_HEIGHT) // CELL_SIZE  # Adjusted for header height
        # track before state
        hidden_before = self.count_hidden()
        mines_remaining_before = self.mines_remaining
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        cell = self.grid[y][x]
        if right_click:
            self.right_clicks += 1
            if cell.state == CellState.HIDDEN:
                cell.state = CellState.FLAGGED
                self.mines_remaining -= 1
            elif cell.state == CellState.FLAGGED:
                cell.state = CellState.HIDDEN
                self.mines_remaining += 1
            return
        self.left_clicks += 1
        if cell.state == CellState.FLAGGED:
            return
        if self.first_click:
            self.place_mines(x, y)
            self.first_click = False
        if cell.is_mine:
            self.handle_game_over((x, y))
        else:
            self.reveal_cell(x, y)
            self.check_victory()
        
        # Track after state 
        hidden_after = self.count_hidden()
        mines_remaining_after = self.mines_remaining

        if hidden_before != hidden_after or mines_remaining_before != mines_remaining_after:
            self.clicks_made += 1

        if not self.game_over:
            self.update_probabilities()
            self.print_board()
            #self.update_probabilities()

    def reveal_all_mines(self):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x].is_mine:
                    self.grid[y][x].state = CellState.REVEALED

    def check_victory(self) -> bool:
        """
        Check if victory conditions are met:
        - All non-mine cells revealed OR
        - All mines correctly flagged
        """
        # Count various cell states
        total_hidden = self.count_hidden()
        total_mines = MINE_COUNT
        total_flags = sum(1 for row in self.grid for cell in row if cell.state == CellState.FLAGGED)
        
        # Victory condition 1: All non-mine cells revealed
        if total_hidden == total_mines:
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    if self.grid[y][x].state == CellState.HIDDEN and not self.grid[y][x].is_mine:
                        return False
            self.handle_victory()
            return True
        
        # Victory condition 2: All mines correctly flagged
        if total_flags == total_mines:
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    cell = self.grid[y][x]
                    if cell.is_mine and cell.state != CellState.FLAGGED:
                        return False
            self.handle_victory()
            return True
        #self.total_moves
        return False

    def handle_victory(self):
        """Handle victory state and display"""
        self.victory = True
        self.game_over = True
        self.show_victory_screen()

    def show_victory_screen(self):
        """Display victory screen with statistics"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((255, 255, 255))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Display victory message and stats
        victory_font = pygame.font.Font(None, 64)
        stats_font = pygame.font.Font(None, 36)
        
        # Victory text
        victory_text = victory_font.render("Victory!", True, DARK_GREEN)
        text_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.screen.blit(victory_text, text_rect)
        
        # Statistics
        stats = [
            f"Time: {self.elapsed_time}s",
            f"Points: {self.points}",
            f"Steps: {self.clicks_made}"
            f"Hints Used: {self.hints_used}",
            f"Total Moves: {self.total_moves}"
        ]
        
        for i, stat in enumerate(stats):
            stat_text = stats_font.render(stat, True, BLACK)
            text_rect = stat_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30 * i)
            )
            self.screen.blit(stat_text, text_rect)

    def check_for_complete_non_mines(self):
        """Check if all non-mine cells are opened"""
        opened_cells = sum(1 for row in self.opened for cell in row if cell)
        total_non_mines = self.grid_size * self.grid_size - self.num_mines
        return opened_cells == total_non_mines

    def auto_mark_remaining_mines(self):
        """Mark all unmarked mines when game is complete"""
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if self.mine_grid[i][j] == 'X' and not self.flagged[i][j]:
                    self.flagged[i][j] = True
                    self.flags_placed += 1

    def draw(self):
        self.screen.fill(GRAY)
        pygame.draw.rect(self.screen, DARK_GRAY, (0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
        
        # Draw buttons on the first line
        self.new_game_button.draw(self.screen, self.font)
        self.restart_button.draw(self.screen, self.font)
        self.quick_start_button.draw(self.screen, self.font)
        self.hint_button.draw(self.screen, self.font)
        self.solve_button.draw(self.screen, self.font)
        self.pause_button.draw(self.screen, self.font)

        # Draw second line of header with seed, time, points, hints
        self.seed_input_box.draw(self.screen)

        timer_text = self.font.render(f"Time: {self.elapsed_time}", True, RED)
        self.screen.blit(timer_text, (120 + PADDING, HEADER_HEIGHT - 35))
        
        points_text = self.font.render(f"Steps: {self.clicks_made}", True, RED)
        self.screen.blit(points_text, (250 + 2 * PADDING, HEADER_HEIGHT - 35))

        hints_text = self.font.render(f"Hints Used: {self.hints_used}", True, RED)
        self.screen.blit(hints_text, (400 + 3 * PADDING, HEADER_HEIGHT - 35))
        
        mines_text = self.font.render(f"Mines: {self.mines_remaining} | Hidden: {self.count_hidden()} ", True, RED)
        self.screen.blit(mines_text, (600 + 4 * PADDING, HEADER_HEIGHT - 35))

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.draw_cell(x, y)

        if self.game_over:
            if self.victory:
                self.draw_message("Victory!")
            else:
                self.draw_message("Game Over!")

        # Add victory message if game won through auto-marking
        if self.victory:
            font = pygame.font.Font(None, 48)
            text = font.render("Victory!", True, (0, 255, 0))
            text_rect = text.get_rect(center=(self.window_size[0]//2, self.window_size[1]//2))
            self.window.blit(text, text_rect)

    def draw_message(self, message):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        text = self.font.render(message, True, WHITE)
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        restart_text = self.font.render("Press R to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        running = True
        self.left_click_held = False
        self.right_click_held = False
        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            self.left_click_held = True
                        elif event.button == 3:
                            self.right_click_held = True

                        if self.left_click_held and self.right_click_held:
                            self.handle_both_clicks(event.pos)

                        elif event.button == 1:
                            if self.new_game_button.handle_event(event):
                                self.reset_game()
                            elif self.restart_button.handle_event(event):
                                self.reset_game(self.seed)
                            elif self.quick_start_button.handle_event(event):
                                self.quick_start()
                            elif self.hint_button.handle_event(event):
                                self.hint()
                            elif self.solve_button.handle_event(event):
                                self.solve_it()
                            elif self.pause_button.handle_event(event):
                                self.toggle_pause()
                            elif event.pos[1] > HEADER_HEIGHT:  # Only process clicks on grid below header
                                self.handle_click(event.pos, event.button == 3)
                        elif event.button == 3:
                            self.handle_click(event.pos, right_click=True)

                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1:
                            self.left_click_held = False
                        elif event.button == 3:
                            self.right_click_held = False

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            self.reset_game()
                            self.quick_start()
                            print("New game started and quick start invoked via 'Q' key.")
                        elif event.key == pygame.K_h:
                            self.hint()
                            print("Hint invoked via 'H' key.")
                        elif event.key == pygame.K_m:
                            if self.mark_probable_mines():
                                print("Marked cells with 100% mine probability.")
                            else:
                                print("No cells with 100% mine probability found.")
                        elif event.key == pygame.K_d:
                            self.print_board()
                        else:
                            seed_input = self.seed_input_box.handle_event(event)
                            if seed_input is not None:
                                self.reset_game(seed_input)

                # Update timer only if the game is active
                if not self.game_over:
                    self.elapsed_time = self.get_game_time()
                self.draw()
                pygame.display.flip()
                self.clock.tick(60)
        except KeyboardInterrupt:
            print("Ctrl+C pressed. Exiting gracefully...")
        finally:
            pygame.quit()
            sys.exit()

        pygame.quit()

    def handle_both_clicks(self, pos):
        """Handle simultaneous left and right clicks for fast reveal and auto-flagging of adjacent cells."""
        self.both_clicks += 1
        x = pos[0] // CELL_SIZE
        y = (pos[1] - HEADER_HEIGHT) // CELL_SIZE

        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            return
        # track before state
        hidden_before = self.count_hidden()
        mines_remaining_before = self.mines_remaining

        cell = self.grid[y][x]
        if cell.state != CellState.REVEALED or cell.is_mine:
            return

        # Check the number of flagged and unflagged neighbors
        flagged_neighbors = 0
        unflagged_neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    neighbor = self.grid[ny][nx]
                    if neighbor.state == CellState.FLAGGED:
                        flagged_neighbors += 1
                    elif neighbor.state == CellState.HIDDEN:
                        unflagged_neighbors.append((nx, ny))

        # Calculate remaining mines to be flagged
        remaining_mines_to_flag = cell.neighbor_mines - flagged_neighbors

        # If remaining unflagged neighbors equals remaining mines, flag unmarked neighbors as mines
        if remaining_mines_to_flag == len(unflagged_neighbors):
            for nx, ny in unflagged_neighbors:
                self.grid[ny][nx].state = CellState.FLAGGED
                self.mines_remaining -= 1  # Adjust mine count

        # If flagged neighbors match the cell's mine count, reveal unflagged neighbors
        elif flagged_neighbors == cell.neighbor_mines:
            for nx, ny in unflagged_neighbors:
                self.reveal_cell(nx, ny)
        self.handle_click(pos)
        # Track after state 
        hidden_after = self.count_hidden()
        mines_remaining_after = self.mines_remaining

        if hidden_before != hidden_after or mines_remaining_before != mines_remaining_after:
            self.clicks_made += 1
        #self.print_board

    def toggle_pause(self):
        current_time = pygame.time.get_ticks()
        if not self.is_paused:
            self.is_paused = True
            self.pause_start_time = current_time
            self.pause_button.update_text("Resume")
            self.pause_button.set_paused(True)
        else:
            self.is_paused = False
            self.total_pause_time += current_time - self.pause_start_time
            self.pause_button.update_text("Pause")
            self.pause_button.set_paused(False)

    def get_game_time(self):
        current_time = pygame.time.get_ticks()
        if self.is_paused:
            return (self.pause_start_time - self.start_time - self.total_pause_time) // 1000
        return (current_time - self.start_time - self.total_pause_time) // 1000

    def count_hidden(self) -> int:
        """
        Count number of cells in HIDDEN state.
        Returns:
            int: Total number of hidden cells in the grid
        """
        return sum(
            1 
            for row in self.grid 
            for cell in row 
            if cell.state == CellState.HIDDEN
        )

    def calculate_base_probability(self):
        """Calculate base probability for all unopened cells"""
        unopened_cells = sum(1 for row in self.grid 
                            for cell in row if cell.state == CellState.HIDDEN)
        if unopened_cells == 0:
            return 0
        return self.mines_remaining / unopened_cells

    def get_adjacent_cells(self, x, y):
        """Get list of adjacent cells"""
        adjacent = []
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:
                    adjacent.append((new_x, new_y))
        return adjacent

    def update_probabilities(self):
        """Update mine probabilities for all cells"""
        # Set base probability for all hidden cells
        base_prob = self.calculate_base_probability()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell.state == CellState.HIDDEN:
                    cell.probability = base_prob

        # Refine probabilities based on revealed numbers
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell.state == CellState.REVEALED and cell.number > 0:
                    adjacent_coords = self.get_adjacent_cells(x, y)
                    hidden_adjacent = [(ax, ay) for ax, ay in adjacent_coords 
                                     if self.grid[ay][ax].state == CellState.HIDDEN]
                    
                    if hidden_adjacent:
                        # Calculate local probability based on remaining mines
                        remaining_adjacent_mines = cell.number - sum(
                            1 for ax, ay in adjacent_coords 
                            if self.grid[ay][ax].state == CellState.FLAGGED
                        )
                        local_prob = remaining_adjacent_mines / len(hidden_adjacent)
                        
                        # Update probabilities of adjacent cells
                        for ax, ay in hidden_adjacent:
                            self.grid[ay][ax].probability = max(
                                self.grid[ay][ax].probability,
                                local_prob
                            )

    def draw_cell(self, x, y):
        cell = self.grid[y][x]
        rect = pygame.Rect(x * CELL_SIZE, 
                          y * CELL_SIZE + HEADER_HEIGHT, 
                          CELL_SIZE, CELL_SIZE)
        
        # Color mapping for numbers
        number_colors = {
            1: BLUE,
            2: DARK_GREEN,
            3: RED,
            4: DARK_BLUE,
            5: DARK_RED,
            6: (0, 128, 128),  # Teal
            7: BLACK,
            8: DARK_GRAY
        }

        # Draw base cell
        if cell.state == CellState.HIDDEN:
            # Hidden cell
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)
            
            # Show probability if game is active
            if not self.game_over:
                prob_text = f"{cell.probability:.2f}"
                prob_surface = self.small_font.render(prob_text, True, BLACK)
                text_rect = prob_surface.get_rect(center=rect.center)
                self.screen.blit(prob_surface, text_rect)

        elif cell.state == CellState.REVEALED:
            # Revealed cell
            pygame.draw.rect(self.screen, WHITE, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)
            
            # Show number if has adjacent mines
            if cell.number > 0:
                color = number_colors.get(cell.number, BLACK)
                number_text = str(cell.number)
                text_surface = self.font.render(number_text, True, color)
                text_rect = text_surface.get_rect(center=rect.center)
                self.screen.blit(text_surface, text_rect)

        elif cell.state == CellState.FLAGGED:
            # Flagged cell
            pygame.draw.rect(self.screen, GRAY, rect)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 1)
            
            # Draw flag
            flag_points = [
                (rect.centerx - 8, rect.centery + 8),
                (rect.centerx - 8, rect.centery - 8),
                (rect.centerx + 4, rect.centery - 4),
                (rect.centerx - 8, rect.centery)
            ]
            pygame.draw.line(self.screen, BLACK, 
                            (rect.centerx - 8, rect.centery + 8),
                            (rect.centerx - 8, rect.centery - 8), 2)
            pygame.draw.polygon(self.screen, RED, flag_points)

        # Show mines on game over
        if self.game_over and cell.is_mine:
            if cell.was_clicked:
                pygame.draw.rect(self.screen, RED, rect)
            pygame.draw.circle(self.screen, BLACK, rect.center, CELL_SIZE // 4)

    def handle_game_over(self, clicked_pos=None):
        """Handle game over state and reveal all mines"""
        self.game_over = True
        
        # Mark clicked mine
        if clicked_pos:
            x, y = clicked_pos
            self.grid[y][x].was_clicked = True
        
        # Reveal all mines
        for row in self.grid:
            for cell in row:
                if cell.is_mine:
                    cell.state = CellState.REVEALED

        # Determine if victory or loss
        if self.victory:
            result = "Victory"
        else:
            result = "Clicked on mine"

        # Count total mines and hidden boxes
        total_mines = sum(1 for row in self.grid for cell in row if cell.is_mine)
        hidden_boxes = sum(1 for row in self.grid for cell in row if cell.state == CellState.HIDDEN)

        # Print game summary
        print(f"Game Over: {result}")
        print(f"Total Mines: {total_mines}")
        print(f"Hidden Boxes: {hidden_boxes}")
        print(f"Left Clicks: {self.left_clicks}")
        print(f"Right Clicks: {self.right_clicks}")
        print(f"Both Clicks: {self.both_clicks}")
        print(f"Total Clicks: {self.left_clicks + self.right_clicks + self.both_clicks}")

    def mark_probable_mines(self):
        """Mark all cells with probability greater than 0.9 as mines."""
        marked_count = 0
        probabilities = self.calculate_mine_probabilities()
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                # Skip if already flagged or revealed
                if cell.state != CellState.HIDDEN:
                    continue

                # Check if probability is 1.0 (or very close due to floating-point precision)
                #probabilities[y][x] = round(probabilities[y][x], 4)
                if probabilities[y][x] >0.1:
                    print(probabilities[y][x],y,x)
                    self.handle_both_clicks((x,y))
                if probabilities[y][x] >= 0.99:
                    if cell.state != CellState.FLAGGED:
                        cell.state = CellState.FLAGGED
                        self.mines_remaining -= 1
                        marked_count += 1

                        if self.debug_mode:
                            print(f"Marked cell at ({x}, {y}) as mine (probability = {probabilities[y][x]:.4f})")

        if self.debug_mode and marked_count == 0:
            print("No cells with probability 1.0 found to mark.")

        return marked_count > 0

    def get_neighbors(self, x, y):
        """Return a list of valid neighbor coordinates for a cell."""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip the cell itself
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    neighbors.append((nx, ny))
        return neighbors

    def calculate_mine_probabilities(self):
        """Calculate the probability of each hidden cell containing a mine."""
        probabilities = [[0.0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell = self.grid[y][x]
                if cell.state != CellState.HIDDEN:
                    continue  # Skip revealed or flagged cells

                neighbors = self.get_neighbors(x, y)
                total_prob = 0.0
                counts = 0

                for nx, ny in neighbors:
                    neighbor_cell = self.grid[ny][nx]
                    if neighbor_cell.state == CellState.REVEALED:
                        # Calculate the number of mines around the revealed cell
                        hidden_neighbors = 0
                        flagged_neighbors = 0
                        neighbor_neighbors = self.get_neighbors(nx, ny)

                        for nnx, nny in neighbor_neighbors:
                            nn_cell = self.grid[nny][nnx]
                            if nn_cell.state == CellState.HIDDEN:
                                hidden_neighbors += 1
                            elif nn_cell.state == CellState.FLAGGED:
                                flagged_neighbors += 1

                        remaining_mines = neighbor_cell.neighbor_mines - flagged_neighbors
                        if hidden_neighbors > 0:
                            prob = remaining_mines / hidden_neighbors
                            total_prob += prob
                            counts += 1

                if counts > 0:
                    probabilities[y][x] = total_prob / counts
                else:
                    probabilities[y][x] = 0.0  # Default probability

        return probabilities

    def draw_header(self):
        """Draw the header with game information."""
        pygame.draw.rect(self.screen, GRAY, (0, 0, WINDOW_WIDTH, HEADER_HEIGHT))
        pygame.draw.rect(self.screen, DARK_GRAY, (0, HEADER_HEIGHT - 2, WINDOW_WIDTH, 2))

        # Display clicks made in the header
        clicks_text = self.small_font.render(f"Left Clicks: {self.left_clicks}", True, BLACK)
        clicks_rect = clicks_text.get_rect(topleft=(PADDING, PADDING))
        self.screen.blit(clicks_text, clicks_rect)

        right_clicks_text = self.small_font.render(f"Right Clicks: {self.right_clicks}", True, BLACK)
        right_clicks_rect = right_clicks_text.get_rect(topleft=(PADDING, PADDING + 20))
        self.screen.blit(right_clicks_text, right_clicks_rect)

        both_clicks_text = self.small_font.render(f"Both Clicks: {self.both_clicks}", True, BLACK)
        both_clicks_rect = both_clicks_text.get_rect(topleft=(PADDING, PADDING + 40))
        self.screen.blit(both_clicks_text, both_clicks_rect)

        total_clicks_text = self.small_font.render(f"Total Clicks: {self.left_clicks + self.right_clicks + self.both_clicks}", True, BLACK)
        total_clicks_rect = total_clicks_text.get_rect(topleft=(PADDING, PADDING + 60))
        self.screen.blit(total_clicks_text, total_clicks_rect)

        points_text = self.small_font.render(f"steps: {self.clicks_made}", True, BLACK)
        points_rect = points_text.get_rect(topleft=(PADDING, PADDING + 80))
        self.screen.blit(points_text, points_rect)

    def find_safe_cell(self):
        """Find a safe cell to reveal as a hint."""
        safe_cells = [(x, y) for y in range(GRID_HEIGHT) for x in range(GRID_WIDTH) if not self.grid[y][x].is_mine and self.grid[y][x].state == CellState.HIDDEN]
        if safe_cells:
            return random.choice(safe_cells)
        return None, None

    def get_quick_start_cells(self):
        """Determine which cells to click during quick start."""
        quick_start_cells = []
        
        # Example logic: Click the center cell
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        quick_start_cells.append((center_x, center_y))
        
        return quick_start_cells
    
    def print_board(self):
        """
        Print the Minesweeper board for debugging purposes.

        Rules:
        - Empty spaces are printed as '0'
        - Flagged cells are printed as 'F'
        - Numeric data (number of nearby mines) is printed as the number
        - Probability ranges:
        * D for 0 < probability <= 0.25
        * C for 0.25 < probability <= 0.5
        * B for 0.5 < probability <= 0.9
        * A for 0.9 < probability <= 1
        """
        for row in self.grid:
            row_str = []
            for cell in row:
                if cell.state == CellState.HIDDEN:
                    prob = cell.probability
                    if prob > 0.99999:
                        row_str.append('A')
                        # mark as mine
                        if cell.state != CellState.FLAGGED:
                            cell.state = CellState.FLAGGED
                            self.mines_remaining -= 1
                        print(f"Marked cell at ({cell.x}, {cell.y}) as mine (probability = {prob:.4f})")
                    elif prob > 0.5:
                        row_str.append('B')
                    elif prob > 0.25:
                        row_str.append('C')
                    elif prob > 0:
                        row_str.append('D')
                    else:
                        row_str.append('0')
                elif cell.state == CellState.FLAGGED:
                    row_str.append('F')
                elif cell.state == CellState.REVEALED:
                    if cell.number > 0:
                        row_str.append(str(cell.number))
                    else:
                        row_str.append('0')
                else:
                    row_str.append('0')
            print(' '.join(row_str))

