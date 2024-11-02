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
            max_tile = self.get_max_tile(data["state"])  # Calculate max tile after the move
            print(f"Move: {direction} | Max Tile: {max_tile}")
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
            max_tile = self.get_max_tile(data["state"])  # Get max tile in the current state
            print("Current Game State:")
            self.print_grid(data["state"])
            print("Score:", data["score"])
            print("Total Moves:", data["total_moves"])
            print("Max Tile:", max_tile)
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

    def get_max_tile(self, grid):
        """Returns the maximum tile value in the current grid."""
        return max(max(row) for row in grid)

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

            # Try moves in priority order and select the first that changes the state
            for move in move_priority:
                result = self.make_move(move)
                if result is not None and result["moved"]:  # Only if a move changes the state
                    time.sleep(0.1)  # Small delay to avoid rapid requests
                    break


# Example usage
if __name__ == "__main__":
    client = Game2048Client()
    # Run the game 25 times
    for i in range(25):
        client.start_game()
        client.solve()
        print("Game", i+1, "completed")
