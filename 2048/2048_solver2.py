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
        self.session_folder = ""

    def start_game(self):
        response = requests.post(f"{self.server_url}/start")
        if response.status_code == 201:
            data = response.json()
            self.game_id = data["game_id"]
            # Create a unique subfolder for the game session
            session_folder_name = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.session_folder = os.path.join(self.screenshot_folder, session_folder_name)
            os.makedirs(self.session_folder, exist_ok=True)
            self.screenshot_count = 0  # Reset screenshot count for this session
            print("New game started!")
            print("Game ID:", self.game_id)
            print("Initial State:")
            self.print_grid(data["state"])
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
            print(f"Move: {direction}")
            self.print_grid(data["state"])
            print("Score:", data["score"])
            print("Total Moves:", data["total_moves"])
            print("Status:", data["status"])
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
            data = response.json()
            print("Current Game State:")
            self.print_grid(data["state"])
            print("Score:", data["score"])
            print("Total Moves:", data["total_moves"])
            print("Status:", data["status"])
            return data
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
            # Format filename as 4-digit sequential numbers (e.g., 0001.png, 0002.png)
            filename = f"{self.screenshot_count:04d}.png"
            screenshot_path = os.path.join(self.session_folder, filename)
            with open(screenshot_path, "wb") as f:
                f.write(response.content)
            print(f"Screenshot saved: {screenshot_path}")
            self.screenshot_count += 1
        else:
            print("Failed to capture screenshot.")
            print(response.json())

    def print_grid(self, grid):
        for row in grid:
            print("\t".join(str(cell) if cell != 0 else "." for cell in row))
        print("\n")

    def evaluate_move(self, grid, direction):
        """
        Evaluate the board state resulting from a move by calculating heuristics:
        - Monotonicity
        - Empty spaces
        - Merges
        """
        monotonicity_score = self.calculate_monotonicity(grid)
        empty_score = self.calculate_empty_spaces(grid)
        merge_score = self.calculate_merges(grid)
        return monotonicity_score + empty_score + merge_score

    def calculate_monotonicity(self, grid):
        """Score based on monotonicity towards the bottom-right corner."""
        score = 0
        for i in range(4):
            for j in range(4):
                if i < 3 and grid[i][j] >= grid[i + 1][j]:  # Vertical
                    score += grid[i][j]
                if j < 3 and grid[i][j] >= grid[i][j + 1]:  # Horizontal
                    score += grid[i][j]
        return score

    def calculate_empty_spaces(self, grid):
        """Count empty spaces (0 values) in the grid."""
        return sum(1 for row in grid for val in row if val == 0)

    def calculate_merges(self, grid):
        """Count possible merges by checking adjacent cells."""
        merges = 0
        for i in range(4):
            for j in range(4):
                if i < 3 and grid[i][j] == grid[i + 1][j]:
                    merges += grid[i][j]
                if j < 3 and grid[i][j] == grid[i][j + 1]:
                    merges += grid[i][j]
        return merges

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
                break
            elif state["status"] == "won":
                print("Congratulations! You've won the game!")
                break

            # Evaluate each move based on heuristics and choose the best one
            best_move = None
            best_score = -float('inf')
            for move in move_priority:
                response = self.make_move(move)
                if response is not None and response["moved"]:
                    score = self.evaluate_move(response["state"], move)
                    if score > best_score:
                        best_score = score
                        best_move = move

            if best_move:
                self.make_move(best_move)
                time.sleep(0.1)  # Small delay to avoid rapid requests

# Example usage
if __name__ == "__main__":
    client = Game2048Client()
    # run the game 25 times
    for i in range(25):
        client.start_game()
        client.solve()
        print("Game", i+1, "completed")
