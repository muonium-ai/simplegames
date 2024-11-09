# main.py

import sys
import importlib
import pygame
import os
from datetime import datetime
import uuid  # To generate a unique identifier
from minesweeper import Minesweeper
from cell import CellState  # Import CellState for setting cell states

def load_solver(solver_name):
    """Dynamically load a solver from the solvers folder."""
    try:
        solver_module = importlib.import_module(f'solvers.{solver_name}')
        SolverClass = getattr(solver_module, 'Solver')
        print(f"Using solver: {solver_name}")
        return SolverClass
    except (ModuleNotFoundError, AttributeError) as e:
        print(f"Error loading solver '{solver_name}': {e}")
        return None

def capture_screenshot(solver_name, iteration, remaining_mines, remaining_hidden, is_victory):
    """Capture a screenshot of the game window and save it to the screenshots folder."""
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:6]  # Unique ID with 6 characters
    victory_prefix = "Victory_" if is_victory else ""
    filename = f"{victory_prefix}{solver_name}_i{iteration:03}_m{remaining_mines:03}_h{remaining_hidden:03}_{timestamp}_{unique_id}.png"
    filepath = os.path.join(screenshots_dir, filename)

    # Capture the screenshot
    screenshot = pygame.display.get_surface()
    pygame.image.save(screenshot, filepath)
    print(f"Screenshot saved as {filepath}")

if __name__ == "__main__":
    solver_name = sys.argv[1] if len(sys.argv) > 1 else None
    debug_mode = "debug" in sys.argv  # Check if 'debug' argument is passed

    SolverClass = load_solver(solver_name) if solver_name else None
    if not SolverClass:
        print("No valid solver provided. Exiting.")
        sys.exit()

    # Initialize the game with the solver and pass debug_mode
    game = Minesweeper(solver=lambda g: SolverClass(g, debug_mode=debug_mode), debug_mode=debug_mode)
    game.iteration = 0  # Track the number of iterations
    is_victory = False  # Track if the game is won

    running = True
    while running:
        game.iteration += 1
        move = game.solver.next_move() if game.solver and not game.game_over else None

        if move:
            x, y, action = move
            if action == 'reveal':
                game.reveal_cell(x, y)
            elif action == 'flag':
                game.grid[y][x].state = CellState.FLAGGED  # Use CellState.FLAGGED
                game.mines_remaining -= 1
                if debug_mode:
                    print(f"Flagged cell at ({x}, {y}) as a mine")

            # Debug output
            remaining_hidden = game.count_hidden_cells()
            if debug_mode or game.game_over:
                print(f"Iteration: {game.iteration} | Remaining Mines: {game.mines_remaining} | Remaining Hidden Cells: {remaining_hidden}")
        else:
            # When no more moves are available, exit the loop
            if not debug_mode:
                # Print final iteration info if no debug mode
                print(f"Iteration: {game.iteration} | Remaining Mines: {game.mines_remaining} | Remaining Hidden Cells: {game.count_hidden_cells()}")
            break

        # Check if all mines have been flagged
        if game.mines_remaining == 0:
            print("Victory")
            is_victory = True
            break

        # Check for quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update display
        game.draw()
        pygame.display.flip()
        game.clock.tick(60)

    # Game over actions
    remaining_hidden = game.count_hidden_cells()
    capture_screenshot(solver_name, game.iteration, game.mines_remaining, remaining_hidden, is_victory)  # Capture screenshot with additional info
    pygame.quit()
    sys.exit()
