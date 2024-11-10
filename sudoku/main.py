# main.py

import argparse
import importlib
import os
import sys
import time
import uuid

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
                        game_over = True
                    else:
                        message = "No moves left"
                        print("No moves left")
                        game_over = True
                else:
                    # Check if the puzzle is solved
                    if grid.is_solved():
                        message = "Victory!"
                        print("Victory")
                        game_over = True
                # Control the speed of the solver if needed
                pygame.time.delay(100)  # Delay in milliseconds
                continue  # Skip event handling when solver is running

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if buttons['new_game'].collidepoint(pos):
                        # New Game button clicked
                        puzzle, solution = generate_puzzle(difficulty)
                        grid = Grid(puzzle, WIDTH, WIDTH)
                        original_board = solution
                        key = None
                        selected_num = None
                        start_time = time.time()
                        message = ""
                        game_over = False
                        # Reset solver and step count
                        if solver:
                            solver.grid = grid
                        step_count = 0
                        # Generate new UUID and directory for screenshots
                        game_uuid = str(uuid.uuid4())
                        screenshots_dir = os.path.join("screenshots", game_uuid)
                        os.makedirs(screenshots_dir, exist_ok=True)
                    elif buttons['hint'].collidepoint(pos) and not game_over:
                        # Hint button clicked
                        if not grid.hint(original_board):
                            message = "No Hints Available"
                        else:
                            message = ""
                            # Check if the puzzle is solved
                            if grid.is_solved():
                                message = "Victory!"
                                print("Victory")
                                game_over = True
                    elif buttons['solve'].collidepoint(pos) and not game_over:
                        # Solve button clicked
                        grid.solve(original_board)
                        game_over = True
                        message = "Puzzle Solved"
                    elif not game_over:
                        if pos[1] >= BUTTON_BAR_HEIGHT + STATUS_BAR_HEIGHT and pos[1] < BUTTON_BAR_HEIGHT + STATUS_BAR_HEIGHT + MENU_BAR_HEIGHT:
                            # Clicked on menu
                            gap = WIDTH / 9
                            x = pos[0] // gap
                            num_clicked = int(x) + 1
                            if selected_num == num_clicked:
                                # Deselect if clicked again
                                selected_num = None
                                grid.unhighlight()
                            else:
                                selected_num = num_clicked
                                grid.unhighlight()
                                grid.highlight(selected_num)
                        elif pos[1] >= TOP_OFFSET:
                            # Clicked on the grid
                            clicked = grid.click(pos)
                            if clicked:
                                row, col = clicked
                                cell = grid.cells[row][col]
                                if cell.editable:
                                    grid.select(row, col)
                                    key = None
                                    message = ""
                            else:
                                grid.selected = None

                if event.type == pygame.KEYDOWN and not game_over:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        key = 1
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        key = 2
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        key = 3
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        key = 4
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        key = 5
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        key = 6
                    if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        key = 7
                    if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        key = 8
                    if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        key = 9
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        key = 0

                    if grid.selected and key is not None:
                        row, col = grid.selected
                        cell = grid.cells[row][col]
                        if cell.editable:
                            if key == 0:
                                cell.value = 0
                                message = ""
                            elif grid.valid(key, row, col):
                                cell.value = key
                                message = ""
                                # Check if the puzzle is solved
                                if grid.is_solved():
                                    message = "Victory!"
                                    print("Victory")
                                    game_over = True  # Set the game_over flag to True
                            else:
                                message = "Invalid Move"
                            key = None

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print("Game interrupted by user.")
        pygame.quit()
        sys.exit()

    pygame.quit()

if __name__ == "__main__":
    main()
