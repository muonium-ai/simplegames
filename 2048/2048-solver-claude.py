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
                    time.sleep(0.1)  # Small delay to avoid rapid requests
                    break




class Advanced2048Solver:
    def __init__(self, depth: int = 3):
        self.DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]
        self.depth = depth
        self.weights = [
            [2**15, 2**14, 2**13, 2**12],
            [2**8, 2**9, 2**10, 2**11],
            [2**7, 2**6, 2**5, 2**4],
            [2**0, 2**1, 2**2, 2**3]
        ]

    def get_empty_cells(self, grid: List[List[int]]) -> List[Tuple[int, int]]:
        empty = []
        for i in range(4):
            for j in range(4):
                if grid[i][j] == 0:
                    empty.append((i, j))
        return empty

    def merge_line(self, line: List[int]) -> Tuple[List[int], int]:
        # Remove zeros and merge identical numbers
        score = 0
        non_zero = [x for x in line if x != 0]
        merged = []
        i = 0
        while i < len(non_zero):
            if i + 1 < len(non_zero) and non_zero[i] == non_zero[i + 1]:
                merged.append(non_zero[i] * 2)
                score += non_zero[i] * 2
                i += 2
            else:
                merged.append(non_zero[i])
                i += 1
        # Pad with zeros
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
                if line_score > 0 or line != merged_line:
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
                if line_score > 0 or line != [new_grid[i][j] for i in range(4)]:
                    moved = True
                for i in range(4):
                    new_grid[i][j] = merged_line[i]
                score += line_score
                
        return new_grid, score, moved

    def monotonicity_score(self, grid: List[List[int]]) -> float:
        """Calculate how well the tiles are ordered (should decrease from top-left to bottom-right)"""
        score = 0
        
        # Horizontal monotonicity
        for i in range(4):
            for j in range(3):
                if grid[i][j] >= grid[i][j + 1] and grid[i][j + 1] != 0:
                    score += 1
                    
        # Vertical monotonicity
        for j in range(4):
            for i in range(3):
                if grid[i][j] >= grid[i + 1][j] and grid[i + 1][j] != 0:
                    score += 1
                    
        return score

    def smoothness_score(self, grid: List[List[int]]) -> float:
        """Calculate how smooth the grid is (adjacent tiles should have similar values)"""
        score = 0
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    val = grid[i][j]
                    # Check horizontal neighbor
                    if j < 3 and grid[i][j + 1] != 0:
                        score -= abs(val - grid[i][j + 1])
                    # Check vertical neighbor
                    if i < 3 and grid[i + 1][j] != 0:
                        score -= abs(val - grid[i + 1][j])
        return score

    def evaluate_position(self, grid: List[List[int]]) -> float:
        """Evaluate the current grid position using multiple heuristics"""
        empty_cells = len(self.get_empty_cells(grid))
        max_tile = max(max(row) for row in grid)
        weighted_sum = sum(grid[i][j] * self.weights[i][j] for i in range(4) for j in range(4))
        monotonicity = self.monotonicity_score(grid)
        smoothness = self.smoothness_score(grid)
        
        # Combine all heuristics with weights
        score = (
            weighted_sum * 1.0 +
            empty_cells * 10000.0 +
            monotonicity * 5000.0 +
            smoothness * 2000.0 +
            max_tile * 100.0
        )
        
        return score

    def expectimax(self, grid: List[List[int]], depth: int, is_max: bool) -> Tuple[float, str]:
        if depth == 0:
            return self.evaluate_position(grid), ""
            
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
            
        else:  # Chance node (computer's turn)
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                return self.evaluate_position(grid), ""
                
            chance_score = 0
            num_empty = len(empty_cells)
            
            # Only try a sample of possible placements to improve performance
            sample_size = min(4, num_empty)
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
        """Get the best move for the current position"""
        _, best_move = self.expectimax(grid, self.depth, True)
        return best_move or random.choice(self.DIRECTIONS)  # Fallback to random if no good move found

class ImprovedGame2048Client(Game2048Client):
    def __init__(self, server_url="http://127.0.0.1:5000"):
        super().__init__(server_url)
        self.solver = Advanced2048Solver(depth=3)

    def solve(self):
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
                # If the best move was invalid, try other moves
                for move in self.solver.DIRECTIONS:
                    if move != best_move:
                        result = self.make_move(move)
                        if result is not None and result["moved"]:
                            break
            
            time.sleep(0.1)  # Small delay to avoid rapid requests

# Example usage
if __name__ == "__main__":
    client = ImprovedGame2048Client()
    # Run the game 25 times
    for i in range(25):
        print(f"\nStarting game {i + 1}")
        client.start_game()
        client.solve()
