import requests
import os
import random
import time

class Game2048Client:
    def __init__(self, server_url="http://127.0.0.1:5000"):
        self.server_url = server_url
        self.game_id = None
        self.screenshot_count = 0
        self.screenshot_folder = "screenshots"

        # Create the screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_folder, exist_ok=True)

    def start_game(self):
        response = requests.post(f"{self.server_url}/start")
        if response.status_code == 201:
            data = response.json()
            self.game_id = data["game_id"]
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
        """Fetches the screenshot from the server and saves it locally with an incremental filename."""
        if self.game_id is None:
            print("Please start a game first.")
            return

        response = requests.get(f"{self.server_url}/screenshot")
        if response.status_code == 200:
            screenshot_path = os.path.join(self.screenshot_folder, f"{self.game_id}_{self.screenshot_count}.png")
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

    def solve(self):
        # Basic greedy strategy
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
    client.start_game()
    client.solve()
