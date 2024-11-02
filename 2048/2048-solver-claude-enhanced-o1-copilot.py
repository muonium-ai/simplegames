import copy
from typing import List, Tuple
import random
import numpy as np
import requests
import os
import time
from datetime import datetime
import math

# Import Numba for JIT compilation
from numba import njit, prange

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

class OptimizedSolver2048:
    def __init__(self, base_depth: int = 3):
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.base_depth = base_depth
        self.transposition_table = {}
        self.move_history = {dir: 0 for dir in self.DIRECTIONS}
        
        # Enhanced weight matrices
        self.corner_weights = np.array([
            [2048, 1024, 512, 256],
            [16, 32, 64, 128],
            [8, 4, 2, 4],
            [0, 0, 0, 0]
        ])
        
        self.snake_weights = np.array([
            [2**15, 2**14, 2**13, 2**12],
            [2**8, 2**9, 2**10, 2**11],
            [2**7, 2**6, 2**5, 2**4],
            [2**0, 2**1, 2**2, 2**3]
        ])

    def evaluate_position(self, grid: List[List[int]], depth_remaining: int) -> float:
        # Cache check
        grid_tuple = tuple(map(tuple, grid))
        if grid_tuple in self.transposition_table:
            return self.transposition_table[grid_tuple]

        empty_cells = len(self.get_empty_cells(grid))
        max_tile = max(max(row) for row in grid)
        stage = self.get_stage(grid)

        # Enhanced scoring components
        corner_score = np.sum(np.multiply(np.array(grid), self.corner_weights))
        snake_score = np.sum(np.multiply(np.array(grid), self.snake_weights))
        gradient_score = self.calculate_gradient_score(grid)
        merge_chains = self.calculate_merge_chains(grid)
        
        # Dynamic weights based on game stage
        weights = self.get_stage_weights(stage)
        
        score = (
            corner_score * weights['corner'] +
            snake_score * weights['snake'] +
            gradient_score * weights['gradient'] +
            merge_chains * weights['merge'] +
            empty_cells * weights['empty'] +
            max_tile * weights['max_tile'] +
            depth_remaining * weights['depth']
        )

        # Cache result
        self.transposition_table[grid_tuple] = score
        return score

    def get_stage_weights(self, stage: str) -> dict:
        if stage == "early":
            return {
                'corner': 2.0, 'snake': 1.0, 'gradient': 1.5,
                'merge': 1.0, 'empty': 2.5, 'max_tile': 1.0,
                'depth': 0.1
            }
        elif stage == "mid":
            return {
                'corner': 2.5, 'snake': 2.0, 'gradient': 2.0,
                'merge': 1.5, 'empty': 2.0, 'max_tile': 1.5,
                'depth': 0.2
            }
        else:
            return {
                'corner': 3.0, 'snake': 2.5, 'gradient': 2.5,
                'merge': 2.0, 'empty': 1.5, 'max_tile': 2.0,
                'depth': 0.3
            }

    def calculate_gradient_score(self, grid: List[List[int]]) -> float:
        score = 0
        for i in range(3):
            for j in range(3):
                if grid[i][j] != 0:
                    # Horizontal gradient
                    if grid[i][j] >= grid[i][j+1]:
                        score += math.log2(grid[i][j])
                    # Vertical gradient    
                    if grid[i][j] >= grid[i+1][j]:
                        score += math.log2(grid[i][j])
        return score

    def calculate_merge_chains(self, grid: List[List[int]]) -> float:
        score = 0
        # Horizontal chains
        for i in range(4):
            chain = 0
            prev = 0
            for j in range(4):
                if grid[i][j] != 0:
                    if grid[i][j] == prev:
                        chain += 1
                        score += chain * math.log2(grid[i][j])
                    prev = grid[i][j]
        
        # Vertical chains
        for j in range(4):
            chain = 0
            prev = 0
            for i in range(4):
                if grid[i][j] != 0:
                    if grid[i][j] == prev:
                        chain += 1
                        score += chain * math.log2(grid[i][j])
                    prev = grid[i][j]
        return score

    def get_dynamic_depth(self, grid: List[List[int]]) -> int:
        empty_cells = len(self.get_empty_cells(grid))
        max_tile = max(max(row) for row in grid)
        
        if max_tile >= 1024 or empty_cells <= 4:
            return self.base_depth + 2
        elif max_tile >= 512 or empty_cells <= 6:
            return self.base_depth + 1
        return self.base_depth

    def expectimax(self, grid: List[List[int]], depth: int, is_max: bool, alpha: float = float('-inf')) -> Tuple[float, str]:
        if depth == 0:
            return self.evaluate_position(grid, depth), ""

        if is_max:
            max_score = float('-inf')
            best_move = ""
            
            # Move ordering based on history
            moves = sorted(self.DIRECTIONS, 
                         key=lambda x: self.move_history[x], 
                         reverse=True)
            
            for direction in moves:
                new_grid, _, moved = self.move_grid(grid, direction)
                if moved:
                    score, _ = self.expectimax(new_grid, depth - 1, False, alpha)
                    if score > max_score:
                        max_score = score
                        best_move = direction
                        alpha = max(alpha, score)
                    
                    # Early cutoff for clearly worse moves
                    if score < alpha / 2:
                        continue
                        
            if best_move:
                self.move_history[best_move] += 1
                
            return max_score, best_move
        else:
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                return self.evaluate_position(grid, depth), ""
                
            avg_score = 0
            total_weight = 0
            
            # Optimized chance node calculation
            for (i, j) in empty_cells:
                for value, prob in [(2, 0.9), (4, 0.1)]:
                    new_grid = [row[:] for row in grid]
                    new_grid[i][j] = value
                    score, _ = self.expectimax(new_grid, depth - 1, True, alpha)
                    avg_score += score * prob
                    total_weight += prob
                    
            return avg_score / total_weight, ""

    def get_best_move(self, grid: List[List[int]]) -> str:
        depth = self.get_dynamic_depth(grid)
        _, best_move = self.expectimax(grid, depth, True)
        
        if not best_move:
            # Fallback to basic moves
            for direction in sorted(self.DIRECTIONS, 
                                 key=lambda x: self.move_history[x],
                                 reverse=True):
                new_grid, _, moved = self.move_grid(grid, direction)
                if moved:
                    return direction
        return best_move

    def get_empty_cells(self, grid: List[List[int]]) -> List[Tuple[int, int]]:
        """Returns list of (row, col) tuples for empty cells."""
        empty = []
        for i in range(4):
            for j in range(4):
                if grid[i][j] == 0:
                    empty.append((i, j))
        return empty

    def get_stage(self, grid: List[List[int]]) -> str:
        """Determines game stage based on max tile and empty cells."""
        max_tile = max(max(row) for row in grid)
        empty_count = len(self.get_empty_cells(grid))
        
        if max_tile < 512 and empty_count > 8:
            return "early"
        elif max_tile < 1024 and empty_count > 4:
            return "mid"
        else:
            return "late"

    def move_grid(self, grid: List[List[int]], direction: str) -> Tuple[List[List[int]], int, bool]:
        """Moves grid in specified direction and returns (new_grid, score, moved)."""
        new_grid = [row[:] for row in grid]
        score = 0
        moved = False
        
        if direction in ["UP", "DOWN"]:
            new_grid = list(map(list, zip(*new_grid)))  # Transpose
        
        if direction in ["DOWN", "RIGHT"]:
            new_grid = [row[::-1] for row in new_grid]  # Reverse
            
        for i in range(4):
            # Compact
            row = [x for x in new_grid[i] if x != 0]
            
            # Merge
            j = 0
            while j < len(row)-1:
                if row[j] == row[j+1]:
                    row[j] *= 2
                    score += row[j]
                    row.pop(j+1)
                    moved = True
                j += 1
                
            # Pad with zeros
            row.extend([0] * (4 - len(row)))
            if row != new_grid[i]:
                moved = True
            new_grid[i] = row
                
        if direction in ["DOWN", "RIGHT"]:
            new_grid = [row[::-1] for row in new_grid]
            
        if direction in ["UP", "DOWN"]:
            new_grid = list(map(list, zip(*new_grid)))
            
        return new_grid, score, moved

class ImprovedGame2048Client(Game2048Client):
    def __init__(self, server_url="http://127.0.0.1:5000"):
        super().__init__(server_url)
        self.solver = OptimizedSolver2048(base_depth=3)  # Base depth for Expectimax

    def solve(self):
        consecutive_failed_moves = 0
        while True:
            state = self.get_state()
            if state is None:
                print("Unable to retrieve game state. Exiting.")
                break

            if state["status"] in ["over", "won"]:
                print(f"Game {state['status']}!")
                self.print_final_stats(state["state"], state["score"],
                                       state["total_moves"], state["status"])
                break

            # Get best move from solver
            best_move = self.solver.get_best_move(state["state"])
            result = self.make_move(best_move)

            if result is None or not result["moved"]:
                consecutive_failed_moves += 1
                # If too many failed moves, try to break out of potential deadlock
                if consecutive_failed_moves >= 3:
                    for move in self.solver.DIRECTIONS:
                        if move != best_move:
                            result = self.make_move(move)
                            if result is not None and result["moved"]:
                                consecutive_failed_moves = 0
                                break
            else:
                consecutive_failed_moves = 0

# Example usage
if __name__ == "__main__":
    client = ImprovedGame2048Client()
    # Run the game multiple times
    for i in range(10):
        print(f"\nStarting game {i + 1}")
        client.start_game()
        client.solve()
