import requests
import os
import time
import math
from datetime import datetime

class Game2048Client:
    def __init__(self, server_url="http://127.0.0.1:5000", depth=3):
        self.server_url = server_url
        self.game_id = None
        self.screenshot_count = 0
        self.screenshot_folder = "screenshots"
        self.depth = depth  # Adjustable depth for Expectimax

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

    # Heuristics
    def weighted_position_heuristic(self, grid):
        """Assigns weights to board positions to keep high tiles in specific areas (e.g., bottom-right)."""
        weights = [
            [4, 3, 2, 1],
            [3, 2, 1, 0.5],
            [2, 1, 0.5, 0.25],
            [1, 0.5, 0.25, 0.125]
        ]
        score = 0
        for i in range(4):
            for j in range(4):
                score += grid[i][j] * weights[i][j]
        return score

    def empty_tile_heuristic(self, grid):
        """Rewards moves that maximize available empty spaces."""
        return sum(row.count(0) for row in grid)

    def monotonicity_heuristic(self, grid):
        """Encourages tile ordering for easier merges."""
        totals = [0, 0]  # row monotonicity, column monotonicity
        for row in grid:
            for i in range(3):
                if row[i] > row[i + 1]:
                    totals[0] += row[i] - row[i + 1]
        for j in range(4):
            for i in range(3):
                if grid[i][j] > grid[i + 1][j]:
                    totals[1] += grid[i][j] - grid[i + 1][j]
        return -min(totals)  # Negative monotonicity

    def combined_heuristic(self, grid):
        """Combines heuristics with assigned weights."""
        return (3 * self.weighted_position_heuristic(grid) +
                2.7 * self.empty_tile_heuristic(grid) +
                1 * self.monotonicity_heuristic(grid))

    # Expectimax algorithm
    def expectimax(self, grid, depth, player_turn):
        """Uses Expectimax with heuristics to select the optimal move."""
        if depth == self.depth or self.get_state()["status"] == "over":
            return self.combined_heuristic(grid), None

        if player_turn:
            max_score = -float('inf')
            best_direction = None
            for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
                simulated_response = self.make_move(direction)
                if simulated_response and simulated_response["moved"]:
                    score, _ = self.expectimax(simulated_response["state"], depth + 1, False)
                    if score > max_score:
                        max_score = score
                        best_direction = direction
            return max_score, best_direction
        else:
            score = 0
            empty_cells = [(r, c) for r in range(4) for c in range(4) if grid[r][c] == 0]
            if not empty_cells:
                return self.combined_heuristic(grid), None
            for cell in empty_cells:
                r, c = cell
                grid[r][c] = 2
                tile_score, _ = self.expectimax(grid, depth + 1, True)
                score += 0.9 * tile_score
                grid[r][c] = 4
                tile_score, _ = self.expectimax(grid, depth + 1, True)
                score += 0.1 * tile_score
                grid[r][c] = 0
            return score / len(empty_cells), None

    def solve(self):
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

            # Use Expectimax to select the best move
            _, best_move = self.expectimax(state["state"], 0, True)
            if best_move:
                self.make_move(best_move)
                time.sleep(0.1)  # Small delay to avoid rapid requests

# Example usage
if __name__ == "__main__":
    client = Game2048Client(depth=3)  # Define the depth as needed
    client.start_game()
    client.solve()
