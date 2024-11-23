import pandas as pd
import random
import os
import uuid
import sys

# Function to generate Minesweeper board
def generate_minesweeper_board(rows, cols, mines, file_path):
    # Initialize board with default values and set dtype to object
    board = pd.DataFrame([[0 for _ in range(cols)] for _ in range(rows)], dtype=object)
    
    # Place mines randomly
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
def generate_multiple_games(n, rows, cols, mines, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for _ in range(n):
        # Generate the board and calculate difficulty
        temp_file_path = os.path.join(folder_path, "temp.txt")
        difficulty_score = generate_minesweeper_board(rows, cols, mines, temp_file_path)
        
        # Generate unique file name with difficulty score at the beginning
        game_uuid = uuid.uuid4().hex[:8]
        final_file_path = os.path.join(folder_path, f"{difficulty_score}_difficulty_{game_uuid}.txt")
        
        # Rename temp file to the final file
        os.rename(temp_file_path, final_file_path)
        
        print(f"Game saved to {final_file_path} with Difficulty Score: {difficulty_score}")

# Main execution
if __name__ == "__main__":
    # Parameters for the game
    rows, cols = 16, 30
    mines = 99
    folder_path = "games"
    
    # Get the number of games from command-line arguments or default to 10
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    # Generate multiple games
    generate_multiple_games(num_games, rows, cols, mines, folder_path)
