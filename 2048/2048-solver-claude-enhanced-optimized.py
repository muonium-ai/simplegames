import copy
from typing import List, Tuple, Dict
import random
import requests
import os
import time
from datetime import datetime

class Game2048Client:
    def __init__(self, server_url="http://127.0.0.1:5000"):
        self.server_url = server_url
        self.game_id = None
        self.screenshot_count = 0
        self.screenshot_folder = "screenshots"

    def start_game(self):
        response = requests.post(f"{self.server_url}/start")
        if response.status_code == 201:
            data = response.json()
            self.game_id = data["game_id"]
            session_folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_folder = os.path.join(self.screenshot_folder, session_folder_name)
            os.makedirs(self.session_folder, exist_ok=True)
            self.screenshot_count = 0
            print("New game started!")
            print("Game ID:", self.game_id)
        else:
            print("Failed to start a new game.")
            print(response.json())

    def make_move(self, direction):
        if self.game_id is None:
            print("Please start a game first.")
            return None
        response = requests.post(f"{self.server_url}/move", json={"direction": direction})
        if response.status_code == 200:
            data = response.json()
            self.capture_screenshot()  # Capture screenshot after each move
            return data
        else:
            print("Failed to make a move.")
            print(response.json())
            return None

    def get_state(self):
        if self.game_id is None:
            print("Please start a game first.")
            return None
        response = requests.get(f"{self.server_url}/state")
        if response.status_code == 200:
            return response.json()
        else:
            print("Failed to retrieve the game state.")
            print(response.json())
            return None

    def capture_screenshot(self):
        """Fetches the screenshot from the server and saves it locally in sequence format."""
        if self.game_id is None:
            print("Please start a game first.")
            return

        response = requests.get(f"{self.server_url}/screenshot")
        if response.status_code == 200:
            filename = f"{self.screenshot_count:04d}.png"
            screenshot_path = os.path.join(self.session_folder, filename)
            with open(screenshot_path, "wb") as f:
                f.write(response.content)
            self.screenshot_count += 1
        else:
            print("Failed to capture screenshot.")
            print(response.json())

    def print_final_stats(self, grid, score, total_moves, status):
        """Prints the final statistics of the game."""
        max_tile = self.get_max_tile(grid)
        print("\nFinal Game Stats:")
        print(f"Max Tile: {max_tile}")
        print(f"Score: {score}")
        print(f"Total Moves: {total_moves}")
        print(f"Status: {status}")
        print("Final Grid:")
        self.print_grid(grid)

    def get_max_tile(self, grid):
        """Returns the maximum tile value in the current grid."""
        return max(max(row) for row in grid)

    def print_grid(self, grid):
        for row in grid:
            print("\t".join(str(cell) if cell != 0 else "." for cell in row))
        print("\n")

    def solve(self):
        move_priority = ["DOWN", "RIGHT", "LEFT", "UP"]
        
        while True:
            state = self.get_state()
            if state is None:
                print("Unable to retrieve game state. Exiting.")
                break
            
            # Check if the game is over or won
            if state["status"] == "over":
                print("Game Over!")
                self.print_final_stats(state["state"], state["score"], state["total_moves"], "over")
                break
            elif state["status"] == "won":
                print("Congratulations! You've won the game!")
                self.print_final_stats(state["state"], state["score"], state["total_moves"], "won")
                break

            # Try moves in priority order and select the first that changes the state
            for move in move_priority:
                result = self.make_move(move)
                if result is not None and result["moved"]:  # Only if a move changes the state
                    #time.sleep(0.1)  # Small delay to avoid rapid requests
                    break




import copy
from typing import List, Tuple, Dict
import random
import numpy as np

import copy
from typing import List, Tuple, Dict
import random
import numpy as np
from dataclasses import dataclass

@dataclass
class MoveResult:
    grid: List[List[int]]
    score: int
    moved: bool
    merges: int
    magnitude: int

class OptimizedSolver2048:
    def __init__(self, depth: int = 4):
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth = depth
        self.cache = {}  # Position cache for duplicate detection
        
        # Dynamic weight matrices
        self.weights = {
            'early': np.array([
                [2**20, 2**19, 2**18, 2**17],
                [2**16, 2**15, 2**14, 2**13],
                [2**9,  2**10, 2**11, 2**12],
                [2**5,  2**6,  2**7,  2**8]
            ]),
            'mid': np.array([
                [2**20, 2**19, 2**18, 2**17],
                [2**17, 2**16, 2**15, 2**14],
                [2**14, 2**13, 2**12, 2**11],
                [2**11, 2**10, 2**9,  2**8]
            ]),
            'late': np.array([
                [2**20, 2**15, 2**14, 2**13],
                [2**19, 2**16, 2**11, 2**8],
                [2**18, 2**17, 2**10, 2**7],
                [2**12, 2**9,  2**6,  2**5]
            ])
        }
        
        # Move sequence patterns that are known to be efficient
        self.preferred_sequences = [
            ["DOWN", "RIGHT"],
            ["RIGHT", "DOWN"],
            ["DOWN", "RIGHT", "DOWN"],
            ["RIGHT", "DOWN", "RIGHT"]
        ]

    def get_grid_hash(self, grid: List[List[int]]) -> str:
        """Create a hash of the grid for caching"""
        return ''.join(str(cell) for row in grid for cell in row)

    def merge_line(self, line: List[int]) -> Tuple[List[int], int, int, int]:
        """Enhanced merge with tracking of merge count and magnitude"""
        score = 0
        merges = 0
        magnitude = 0  # Track the size of merges
        merged = []
        line = [x for x in line if x != 0]
        i = 0
        while i < len(line):
            if i + 1 < len(line) and line[i] == line[i + 1]:
                merged_value = line[i] * 2
                merged.append(merged_value)
                score += merged_value
                merges += 1
                magnitude += np.log2(merged_value)  # Log scale for merge magnitude
                i += 2
            else:
                merged.append(line[i])
                i += 1
        merged.extend([0] * (4 - len(merged)))
        return merged, score, merges, magnitude

    def move_grid(self, grid: List[List[int]], direction: str) -> MoveResult:
        """Enhanced move function that returns detailed move results"""
        new_grid = [row[:] for row in grid]
        total_score = 0
        total_merges = 0
        total_magnitude = 0
        moved = False
        
        if direction in ["LEFT", "RIGHT"]:
            for i in range(4):
                line = new_grid[i][:]
                if direction == "RIGHT":
                    line.reverse()
                merged_line, score, merges, magnitude = self.merge_line(line)
                if direction == "RIGHT":
                    merged_line.reverse()
                if merged_line != new_grid[i]:
                    moved = True
                new_grid[i] = merged_line
                total_score += score
                total_merges += merges
                total_magnitude += magnitude
        else:  # UP or DOWN
            for j in range(4):
                line = [new_grid[i][j] for i in range(4)]
                if direction == "DOWN":
                    line.reverse()
                merged_line, score, merges, magnitude = self.merge_line(line)
                if direction == "DOWN":
                    merged_line.reverse()
                if moved or merged_line != [new_grid[i][j] for i in range(4)]:
                    moved = True
                for i in range(4):
                    new_grid[i][j] = merged_line[i]
                total_score += score
                total_merges += merges
                total_magnitude += magnitude
        
        return MoveResult(new_grid, total_score, moved, total_merges, total_magnitude)

    def evaluate_sequence_potential(self, grid: List[List[int]], sequence: List[str]) -> float:
        """Evaluate potential of a move sequence"""
        current_grid = [row[:] for row in grid]
        total_score = 0
        total_merges = 0
        total_magnitude = 0
        
        for direction in sequence:
            result = self.move_grid(current_grid, direction)
            if not result.moved:
                return float('-inf')
            current_grid = result.grid
            total_score += result.score
            total_merges += result.merges
            total_magnitude += result.magnitude
        
        return total_score + (total_merges * 100) + (total_magnitude * 50)

    def get_empty_cells(self, grid: List[List[int]]) -> List[Tuple[int, int]]:
        return [(i, j) for i in range(4) for j in range(4) if grid[i][j] == 0]

    def evaluate_position(self, grid: List[List[int]], moves_made: int) -> float:
        """Enhanced position evaluation with move efficiency consideration"""
        max_tile = max(max(row) for row in grid)
        empty_count = len(self.get_empty_cells(grid))
        
        # Determine game stage
        stage = 'early' if max_tile <= 256 else 'mid' if max_tile <= 1024 else 'late'
        weights = self.weights[stage]
        
        # Calculate base weighted sum
        weighted_sum = sum(grid[i][j] * weights[i][j] for i in range(4) for j in range(4))
        
        # Evaluate move efficiency
        efficiency_penalty = moves_made * 10  # Penalize longer solutions
        
        # Calculate merge potential
        merge_potential = 0
        for i in range(4):
            for j in range(3):
                if grid[i][j] == grid[i][j + 1] and grid[i][j] != 0:
                    merge_potential += grid[i][j]
        for i in range(3):
            for j in range(4):
                if grid[i][j] == grid[i + 1][j] and grid[i][j] != 0:
                    merge_potential += grid[i][j]
        
        # Corner bonus
        corner_bonus = 0
        corners = [(0, 0), (0, 3), (3, 0), (3, 3)]
        for i, j in corners:
            if grid[i][j] == max_tile:
                corner_bonus = max_tile * 2
        
        return (weighted_sum * 1.0 +
                empty_count * 10000.0 +
                merge_potential * 1000.0 +
                corner_bonus -
                efficiency_penalty)

    def expectimax(self, grid: List[List[int]], depth: int, moves_made: int, is_max: bool) -> Tuple[float, str]:
        grid_hash = self.get_grid_hash(grid)
        cache_key = (grid_hash, depth, is_max)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        if depth == 0:
            score = self.evaluate_position(grid, moves_made)
            self.cache[cache_key] = (score, "")
            return score, ""
            
        if is_max:
            max_score = float('-inf')
            best_move = ""
            
            # First try preferred sequences
            for sequence in self.preferred_sequences:
                sequence_score = self.evaluate_sequence_potential(grid, sequence)
                if sequence_score > max_score:
                    current_grid = [row[:] for row in grid]
                    valid_sequence = True
                    for direction in sequence:
                        result = self.move_grid(current_grid, direction)
                        if not result.moved:
                            valid_sequence = False
                            break
                        current_grid = result.grid
                    if valid_sequence:
                        max_score = sequence_score
                        best_move = sequence[0]
            
            # Then try individual moves
            for direction in self.DIRECTIONS:
                result = self.move_grid(grid, direction)
                if result.moved:
                    score, _ = self.expectimax(result.grid, depth - 1, moves_made + 1, False)
                    score += result.magnitude * 100  # Bonus for efficient merges
                    if score > max_score:
                        max_score = score
                        best_move = direction
            
            self.cache[cache_key] = (max_score, best_move)
            return max_score, best_move
        else:
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                score = self.evaluate_position(grid, moves_made)
                self.cache[cache_key] = (score, "")
                return score, ""
            
            chance_score = 0
            sample_size = min(4, len(empty_cells))
            sampled_cells = random.sample(empty_cells, sample_size)
            
            for pos in sampled_cells:
                for value in [2, 4]:
                    prob = 0.9 if value == 2 else 0.1
                    new_grid = [row[:] for row in grid]
                    new_grid[pos[0]][pos[1]] = value
                    score, _ = self.expectimax(new_grid, depth - 1, moves_made, True)
                    chance_score += score * prob / sample_size
            
            self.cache[cache_key] = (chance_score, "")
            return chance_score, ""

    def get_best_move(self, grid: List[List[int]], moves_made: int) -> str:
        """Get best move with move count optimization"""
        self.cache.clear()  # Clear cache for new search
        _, best_move = self.expectimax(grid, self.depth, moves_made, True)
        return best_move or random.choice(self.DIRECTIONS)

class OptimizedGame2048Client(Game2048Client):
    def __init__(self, server_url="http://127.0.0.1:5000"):
        super().__init__(server_url)
        self.solver = OptimizedSolver2048(depth=4)
        self.moves_made = 0

    def solve(self):
        self.moves_made = 0
        consecutive_failed_moves = 0
        
        while True:
            state = self.get_state()
            if state is None:
                print("Unable to retrieve game state. Exiting.")
                break
            
            if state["status"] in ["over", "won"]:
                print(f"Game {state['status']}!")
                print(f"Solved in {self.moves_made} moves!")
                self.print_final_stats(state["state"], state["score"], 
                                     state["total_moves"], state["status"])
                break

            best_move = self.solver.get_best_move(state["state"], self.moves_made)
            result = self.make_move(best_move)
            
            if result is None or not result["moved"]:
                consecutive_failed_moves += 1
                if consecutive_failed_moves >= 2:
                    # Try alternative moves if stuck
                    for move in self.solver.DIRECTIONS:
                        if move != best_move:
                            result = self.make_move(move)
                            if result is not None and result["moved"]:
                                self.moves_made += 1
                                consecutive_failed_moves = 0
                                break
            else:
                self.moves_made += 1
                consecutive_failed_moves = 0
            
            time.sleep(0.1)

# Example usage
if __name__ == "__main__":
    client = OptimizedGame2048Client()
    # Run the game 25 times
    for i in range(25):
        print(f"\nStarting game {i + 1}")
        client.start_game()
        client.solve()