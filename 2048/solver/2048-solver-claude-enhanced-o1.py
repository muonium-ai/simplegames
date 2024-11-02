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

class EnhancedSolver2048:
    def __init__(self, base_depth: int = 3):
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.base_depth = base_depth
        # Enhanced weight matrix focusing more strongly on corner strategy
        self.weights = np.array([
            [65536, 32768, 16384, 8192],
            [256, 512, 1024, 4096],
            [128, 64, 32, 16],
            [8, 4, 2, 1]
        ])

    def get_empty_cells(self, grid: List[List[int]]) -> List[Tuple[int, int]]:
        return [(i, j) for i in range(4) for j in range(4) if grid[i][j] == 0]

    def merge_line(self, line: List[int]) -> Tuple[List[int], int]:
        score = 0
        merged = []
        line = [x for x in line if x != 0]
        i = 0
        while i < len(line):
            if i + 1 < len(line) and line[i] == line[i + 1]:
                merged.append(line[i] * 2)
                score += line[i] * 2
                i += 2
            else:
                merged.append(line[i])
                i += 1
        merged.extend([0] * (4 - len(merged)))
        return merged, score

    def move_grid(self, grid: List[List[int]], direction: str) -> Tuple[List[List[int]], int, bool]:
        new_grid = [row[:] for row in grid]
        score = 0
        moved = False

        if direction in ["LEFT", "RIGHT"]:
            for i in range(4):
                line = new_grid[i][:]
                if direction == "RIGHT":
                    line.reverse()
                merged_line, line_score = self.merge_line(line)
                if direction == "RIGHT":
                    merged_line.reverse()
                if merged_line != new_grid[i]:
                    moved = True
                new_grid[i] = merged_line
                score += line_score
        else:  # UP or DOWN
            for j in range(4):
                line = [new_grid[i][j] for i in range(4)]
                if direction == "DOWN":
                    line.reverse()
                merged_line, line_score = self.merge_line(line)
                if direction == "DOWN":
                    merged_line.reverse()
                if merged_line != [new_grid[i][j] for i in range(4)]:
                    moved = True
                for i in range(4):
                    new_grid[i][j] = merged_line[i]
                score += line_score

        return new_grid, score, moved

    def get_stage(self, grid: List[List[int]]) -> str:
        """Determine game stage based on max tile and empty cells"""
        max_tile = max(max(row) for row in grid)
        empty_count = len(self.get_empty_cells(grid))

        if max_tile <= 256 or empty_count >= 8:
            return "early"
        elif max_tile <= 1024 or empty_count >= 4:
            return "mid"
        else:
            return "late"

    def monotonicity_score(self, grid: List[List[int]]) -> float:
        """Enhanced monotonicity scoring with directional bias"""
        score = 0
        # Horizontal monotonicity
        for i in range(4):
            current = [grid[i][j] for j in range(4)]
            current = [math.log2(val) if val != 0 else 0 for val in current]
            for k in range(3):
                diff = current[k] - current[k + 1]
                score += diff if diff > 0 else -diff
        # Vertical monotonicity
        for j in range(4):
            current = [grid[i][j] for i in range(4)]
            current = [math.log2(val) if val != 0 else 0 for val in current]
            for k in range(3):
                diff = current[k] - current[k + 1]
                score += diff if diff > 0 else -diff
        return -score  # Negative because we want to minimize differences

    def smoothness_score(self, grid: List[List[int]]) -> float:
        """Calculate smoothness with logarithmic differences"""
        score = 0
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    val = math.log2(grid[i][j])
                    # Check horizontal neighbor
                    if j < 3 and grid[i][j + 1] != 0:
                        target = math.log2(grid[i][j + 1])
                        score -= abs(val - target)
                    # Check vertical neighbor
                    if i < 3 and grid[i + 1][j] != 0:
                        target = math.log2(grid[i + 1][j])
                        score -= abs(val - target)
        return score

    def merge_potential_score(self, grid: List[List[int]]) -> float:
        """Calculate potential for merging tiles"""
        score = 0
        # Horizontal merges
        for i in range(4):
            for j in range(3):
                if grid[i][j] != 0 and grid[i][j] == grid[i][j + 1]:
                    score += grid[i][j]
        # Vertical merges
        for i in range(3):
            for j in range(4):
                if grid[i][j] != 0 and grid[i][j] == grid[i + 1][j]:
                    score += grid[i][j]
        return score

    def evaluate_position(self, grid: List[List[int]], depth_remaining: int) -> float:
        """Enhanced position evaluation with dynamic weights"""
        empty_cells = len(self.get_empty_cells(grid))
        max_tile = max(max(row) for row in grid)

        # Calculate base scores
        weighted_grid = np.multiply(np.array(grid), self.weights)
        weighted_sum = np.sum(weighted_grid)
        monotonicity = self.monotonicity_score(grid)
        smoothness = self.smoothness_score(grid)
        merge_potential = self.merge_potential_score(grid)

        # Dynamic weight adjustments based on game stage
        stage = self.get_stage(grid)
        if stage == "early":
            empty_weight = 27000
            mono_weight = 10000
            smooth_weight = 10000
            merge_weight = 5000
        elif stage == "mid":
            empty_weight = 25000
            mono_weight = 12000
            smooth_weight = 12000
            merge_weight = 8000
        else:
            empty_weight = 22000
            mono_weight = 14000
            smooth_weight = 15000
            merge_weight = 10000

        # Combine all heuristics with dynamic weights
        score = (
            weighted_sum +
            empty_cells * empty_weight +
            monotonicity * mono_weight +
            smoothness * smooth_weight +
            merge_potential * merge_weight +
            max_tile * 1000.0 +
            depth_remaining * 10.0  # Bonus for maintaining options
        )

        return score

    def expectimax(self, grid: List[List[int]], depth: int, is_max: bool) -> Tuple[float, str]:
        if depth == 0:
            return self.evaluate_position(grid, depth), ""

        if is_max:
            max_score = float('-inf')
            best_move = ""
            for direction in self.DIRECTIONS:
                new_grid, _, moved = self.move_grid(grid, direction)
                if moved:
                    score, _ = self.expectimax(new_grid, depth - 1, False)
                    if score > max_score:
                        max_score = score
                        best_move = direction
            return max_score, best_move
        else:
            # Chance node
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                return self.evaluate_position(grid, depth), ""
            scores = []
            for (i, j) in empty_cells:
                for value, prob in [(2, 0.9), (4, 0.1)]:
                    new_grid = [row[:] for row in grid]
                    new_grid[i][j] = value
                    score, _ = self.expectimax(new_grid, depth - 1, True)
                    scores.append(score * prob)
            avg_score = sum(scores) / len(scores)
            return avg_score, ""

    def get_best_move(self, grid: List[List[int]]) -> str:
        """Get best move with dynamic depth based on game stage and processing power"""
        stage = self.get_stage(grid)
        if stage == "early":
            depth = self.base_depth
        elif stage == "mid":
            depth = self.base_depth + 1  # Look deeper in mid-game
        else:
            depth = self.base_depth + 2  # Look even deeper in late-game

        # Limit depth based on available processing power
        max_depth = 5  # Adjust this based on your system's capabilities
        depth = min(depth, max_depth)

        _, best_move = self.expectimax(grid, depth, True)
        if not best_move:
            # Fallback strategy if no good move found
            for direction in self.DIRECTIONS:
                new_grid, _, moved = self.move_grid(grid, direction)
                if moved:
                    return direction
        return best_move

class ImprovedGame2048Client(Game2048Client):
    def __init__(self, server_url="http://127.0.0.1:5000"):
        super().__init__(server_url)
        self.solver = EnhancedSolver2048(base_depth=3)  # Base depth for Expectimax

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
