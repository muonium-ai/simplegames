import pandas as pd
import random
import os
import uuid
import sys


# Function to generate Minesweeper board
def generate_minesweeper_board(rows, cols, mines, file_path, seed=None):
    # Initialize board with default values and set dtype to object
    board = pd.DataFrame([[0 for _ in range(cols)] for _ in range(rows)], dtype=object)
    
    # Place mines based on seed or randomly
    if seed:
        random.seed(seed)
    mine_positions = set()
    while len(mine_positions) < mines:
        r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
        mine_positions.add((r, c))
    
    for r, c in mine_positions:
        board.iloc[r, c] = '*'  # Assign mines as strings
    
    # Function to calculate adjacent mines
    def count_adjacent_mines(r, c):
        if board.iloc[r, c] == '*':
            return '*'
        adjacent_cells = [
            (r + dr, c + dc)
            for dr in [-1, 0, 1]
            for dc in [-1, 0, 1]
            if (dr != 0 or dc != 0) and 0 <= r + dr < rows and 0 <= c + dc < cols
        ]
        return sum(1 for ar, ac in adjacent_cells if board.iloc[ar, ac] == '*')
    
    # Update board with adjacent mine counts
    for r in range(rows):
        for c in range(cols):
            if board.iloc[r, c] != '*':
                board.iloc[r, c] = count_adjacent_mines(r, c)
    
    # Save board to text file
    with open(file_path, 'w') as f:
        for row in board.values:
            f.write(''.join(str(cell) for cell in row) + '\n')
    
    # Count 0's and each digit
    counts = {str(i): 0 for i in range(9)}
    for row in board.values.flatten():
        if row != '*':
            counts[str(row)] += 1
    
    # Calculate difficulty score
    difficulty_score = sum(int(k) * v for k, v in counts.items())
    return difficulty_score


# Function to generate multiple Minesweeper games
def generate_multiple_games(n, rows, cols, mines, folder_path, seed=None):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for _ in range(n):
        # Generate the board and calculate difficulty
        temp_file_path = os.path.join(folder_path, "temp.txt")
        difficulty_score = generate_minesweeper_board(rows, cols, mines, temp_file_path, seed=seed)
        
        # Generate unique file name with difficulty score at the beginning
        game_uuid = uuid.uuid4().hex[:8]
        final_file_path = os.path.join(folder_path, f"{difficulty_score}_difficulty_{game_uuid}.txt")
        
        # Rename temp file to the final file
        os.rename(temp_file_path, final_file_path)
        
        print(f"Game saved to {final_file_path} with Difficulty Score: {difficulty_score}")


# Function to simplify an existing game
def simplify_game(seed_file, reduced_mines, folder_path):
    # Load the seed board
    with open(seed_file, 'r') as f:
        seed_lines = f.readlines()
    
    # Use seed lines to determine rows and cols
    rows = len(seed_lines)
    cols = len(seed_lines[0].strip())
    seed = hash(''.join(seed_lines))  # Create a reproducible seed from the file
    
    # Generate a new game with reduced mines
    generate_multiple_games(1, rows, cols, reduced_mines, folder_path, seed=seed)


# Main execution
if __name__ == "__main__":
    # Parameters for the game
    rows, cols = 16, 30
    default_mines = 99
    folder_path = "games"
    
    # Parse command-line arguments
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    mines = int(sys.argv[2]) if len(sys.argv) > 2 else default_mines
    seed_file = sys.argv[3] if len(sys.argv) > 3 else None  # Optional seed file for simplification
    
    if seed_file:
        # Simplify an existing game
        reduced_mines = int(sys.argv[4]) if len(sys.argv) > 4 else (mines - 1)
        simplify_game(seed_file, reduced_mines, folder_path)
    else:
        # Generate multiple games
        generate_multiple_games(num_games, rows, cols, mines, folder_path)
