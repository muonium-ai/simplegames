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

class EnhancedSolver2048:
    def __init__(self, depth: int = 4):
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth = depth
        # Enhanced weight matrix focusing more strongly on corner strategy
        self.weights = np.array([
            [2**20, 2**19, 2**18, 2**17],
            [2**16, 2**15, 2**14, 2**13],
            [2**9,  2**10, 2**11, 2**12],
            [2**5,  2**6,  2**7,  2**8]
        ])
        
        # Corner-specific weight matrices for different stages
        self.early_weights = np.array([
            [2**20, 2**19, 2**18, 2**17],
            [2**16, 2**15, 2**14, 2**13],
            [2**9,  2**10, 2**11, 2**12],
            [2**5,  2**6,  2**7,  2**8]
        ])
        
        self.mid_weights = np.array([
            [2**20, 2**19, 2**18, 2**17],
            [2**17, 2**16, 2**15, 2**14],
            [2**14, 2**13, 2**12, 2**11],
            [2**11, 2**10, 2**9,  2**8]
        ])
        
        self.late_weights = np.array([
            [2**20, 2**15, 2**14, 2**13],
            [2**19, 2**16, 2**11, 2**8],
            [2**18, 2**17, 2**10, 2**7],
            [2**12, 2**9,  2**6,  2**5]
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
                if moved or merged_line != [new_grid[i][j] for i in range(4)]:
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

    def get_weight_matrix(self, grid: List[List[int]]) -> np.ndarray:
        """Get appropriate weight matrix based on game stage"""
        stage = self.get_stage(grid)
        if stage == "early":
            return self.early_weights
        elif stage == "mid":
            return self.mid_weights
        else:
            return self.late_weights

    def monotonicity_score(self, grid: List[List[int]]) -> float:
        """Enhanced monotonicity scoring with directional bias"""
        score = 0
        
        # Horizontal monotonicity (left to right)
        for i in range(4):
            prev = grid[i][0]
            for j in range(1, 4):
                if grid[i][j] != 0:
                    if prev >= grid[i][j]:
                        score += np.log2(prev) if prev > 0 else 0
                    else:
                        score -= np.log2(grid[i][j])
                    prev = grid[i][j]
        
        # Vertical monotonicity (top to bottom)
        for j in range(4):
            prev = grid[0][j]
            for i in range(1, 4):
                if grid[i][j] != 0:
                    if prev >= grid[i][j]:
                        score += np.log2(prev) if prev > 0 else 0
                    else:
                        score -= np.log2(grid[i][j])
                    prev = grid[i][j]
        
        return score

    def smoothness_score(self, grid: List[List[int]]) -> float:
        """Calculate smoothness with logarithmic differences"""
        score = 0
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    val = np.log2(grid[i][j])
                    # Check horizontal neighbor
                    if j < 3 and grid[i][j + 1] != 0:
                        score -= abs(val - np.log2(grid[i][j + 1]))
                    # Check vertical neighbor
                    if i < 3 and grid[i + 1][j] != 0:
                        score -= abs(val - np.log2(grid[i + 1][j]))
        return score

    def merge_potential_score(self, grid: List[List[int]]) -> float:
        """Calculate potential for merging tiles"""
        score = 0
        # Horizontal merges
        for i in range(4):
            for j in range(3):
                if grid[i][j] != 0 and grid[i][j] == grid[i][j + 1]:
                    score += grid[i][j] * 2
        
        # Vertical merges
        for i in range(3):
            for j in range(4):
                if grid[i][j] != 0 and grid[i][j] == grid[i + 1][j]:
                    score += grid[i][j] * 2
        
        return score

    def corner_proximity_score(self, grid: List[List[int]]) -> float:
        """Score based on high values being close to corners"""
        score = 0
        max_val = max(max(row) for row in grid)
        if max_val == grid[0][0]:  # Top-left corner
            score += max_val * 4
        elif max_val == grid[0][3]:  # Top-right corner
            score += max_val * 3
        elif max_val == grid[3][0]:  # Bottom-left corner
            score += max_val * 2
        elif max_val == grid[3][3]:  # Bottom-right corner
            score += max_val
        return score

    def evaluate_position(self, grid: List[List[int]], depth_remaining: int) -> float:
        """Enhanced position evaluation with dynamic weights"""
        weight_matrix = self.get_weight_matrix(grid)
        empty_cells = len(self.get_empty_cells(grid))
        max_tile = max(max(row) for row in grid)
        
        # Calculate base scores
        weighted_sum = sum(grid[i][j] * weight_matrix[i][j] for i in range(4) for j in range(4))
        monotonicity = self.monotonicity_score(grid)
        smoothness = self.smoothness_score(grid)
        merge_potential = self.merge_potential_score(grid)
        corner_score = self.corner_proximity_score(grid)
        
        # Dynamic weight adjustments based on game stage
        stage = self.get_stage(grid)
        if stage == "early":
            empty_weight = 20000
            mono_weight = 10000
            smooth_weight = 5000
            merge_weight = 15000
            corner_weight = 25000
        elif stage == "mid":
            empty_weight = 15000
            mono_weight = 15000
            smooth_weight = 10000
            merge_weight = 20000
            corner_weight = 30000
        else:
            empty_weight = 10000
            mono_weight = 20000
            smooth_weight = 15000
            merge_weight = 25000
            corner_weight = 35000
        
        # Combine all heuristics with dynamic weights
        score = (
            weighted_sum * 1.0 +
            empty_cells * empty_weight +
            monotonicity * mono_weight +
            smoothness * smooth_weight +
            merge_potential * merge_weight +
            corner_score * corner_weight +
            max_tile * 1000.0 +
            depth_remaining * 100.0  # Bonus for maintaining options
        )
        
        return score

    def expectimax(self, grid: List[List[int]], depth: int, is_max: bool) -> Tuple[float, str]:
        if depth == 0:
            return self.evaluate_position(grid, depth), ""
            
        if is_max:
            max_score = float('-inf')
            best_move = ""
            
            # Try each direction
            for direction in self.DIRECTIONS:
                new_grid, _, moved = self.move_grid(grid, direction)
                if moved:
                    score, _ = self.expectimax(new_grid, depth - 1, False)
                    if score > max_score:
                        max_score = score
                        best_move = direction
            
            return max_score, best_move
            
        else:  # Chance node (computer's turn)
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                return self.evaluate_position(grid, depth), ""
            
            chance_score = 0
            num_empty = len(empty_cells)
            
            # Improved sampling strategy for chance nodes
            sample_size = min(6, num_empty)  # Increased sample size
            sampled_cells = random.sample(empty_cells, sample_size)
            
            for pos in sampled_cells:
                for value in [2, 4]:
                    prob = 0.9 if value == 2 else 0.1
                    new_grid = [row[:] for row in grid]
                    new_grid[pos[0]][pos[1]] = value
                    score, _ = self.expectimax(new_grid, depth - 1, True)
                    chance_score += score * prob / sample_size
            
            return chance_score, ""

    def get_best_move(self, grid: List[List[int]]) -> str:
        """Get best move with dynamic depth based on game stage"""
        stage = self.get_stage(grid)
        if stage == "early":
            depth = self.depth
        elif stage == "mid":
            depth = self.depth + 1  # Look deeper in mid-game
        else:
            depth = self.depth + 2  # Look even deeper in late-game
            
        _, best_move = self.expectimax(grid, depth, True)
        if not best_move:
            # Fallback strategy if no good move found
            for direction in ["DOWN", "RIGHT", "LEFT", "UP"]:
                _, _, moved = self.move_grid(grid, direction)
                if moved:
                    return direction
        return best_move

class ImprovedGame2048Client(Game2048Client):
    def __init__(self, server_url="http://127.0.0.1:5000"):
        super().__init__(server_url)
        self.solver = EnhancedSolver2048(depth=4)  # Increased base depth

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
            
            #time.sleep(0.1)

# Example usage
if __name__ == "__main__":
    client = ImprovedGame2048Client()
    # Run the game 25 times
    for i in range(25):
        print(f"\nStarting game {i + 1}")
        client.start_game()
        client.solve()