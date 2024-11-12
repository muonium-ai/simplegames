# main.py

import argparse
import importlib
import os
import sys
import time
import uuid
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame

from lib.config import WIDTH, HEIGHT, WHITE, BUTTON_BAR_HEIGHT, STATUS_BAR_HEIGHT, MENU_BAR_HEIGHT, TOP_OFFSET
from lib.grid import Grid
from lib.utils import redraw_window
from lib.generator import generate_puzzle

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Sudoku Game with Solver")
    parser.add_argument("--solver", type=str, help="Name of the solver to use")
    args = parser.parse_args()

    # Generate UUID for the game session
    game_uuid = str(uuid.uuid4())
    screenshots_dir = os.path.join("screenshots", game_uuid)
    os.makedirs(screenshots_dir, exist_ok=True)

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku Game")

    run = True
    difficulty = 5  # Adjust this value for different difficulty levels

    # Generate puzzle and solution
    puzzle, solution = generate_puzzle(difficulty)
    grid = Grid(puzzle, WIDTH, WIDTH)
    original_board = solution  # Keep the solution for hints and solving
    key = None
    selected_num = None
    start_time = time.time()
    message = ""
    game_over = False  # Flag to indicate if the game is over

    solver = None
    step_count = 0

    if args.solver:
        # Load the solver dynamically
        try:
            solver_module = importlib.import_module(f"solvers.{args.solver}")
            solver = solver_module.Solver(grid)
            print(f"Using solver: {args.solver}")
        except ImportError:
            print(f"Solver '{args.solver}' not found.")
            sys.exit(1)

    try:
        while run:
            # Stop updating the elapsed time when the game is over
            if not game_over:
                elapsed_time = time.time() - start_time
            else:
                # Freeze the time when the game is won
                elapsed_time = elapsed_time

            # Get button rectangles from redraw_window
            buttons = redraw_window(WIN, grid, selected_num, elapsed_time, message, game_over)

            # Take screenshot
            screenshot_path = os.path.join(screenshots_dir, f"step_{step_count:03d}.png")
            pygame.image.save(WIN, screenshot_path)
            step_count += 1

            if solver and not game_over:
                # Automated solver is active
                move_made = solver.next_move()
                if not move_made:
                    # No moves left or puzzle is solved
                    if grid.is_solved():
                        message = "Victory!"
                        print("Victory")
                    else:
                        message = "No moves left"
                        print("No moves left")
                    game_over = True
                    run = False  # Exit the game loop
                else:
                    # Check if the puzzle is solved
                    if grid.is_solved():
                        message = "Victory!"
                        print("Victory")
                        game_over = True
                        run = False  # Exit the game loop
                # Control the speed of the solver if needed
                pygame.time.delay(100)  # Delay in milliseconds
                continue  # Skip event handling when solver is running

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()

                # ... existing event handling code for user input ...

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Game interrupted by user.")
        pygame.quit()
        sys.exit()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
