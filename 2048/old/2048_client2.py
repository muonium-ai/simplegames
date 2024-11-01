import requests
import random

class Game2048Client:
    def __init__(self, server_url="http://127.0.0.1:5000"):
        self.server_url = server_url
        self.game_id = None

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
            print("Status:", data["status"])
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
            print("Status:", data["status"])
            return data
        else:
            print("Failed to retrieve the game state.")
            print(response.json())
            return None

    def print_grid(self, grid):
        for row in grid:
            print("\t".join(str(cell) if cell != 0 else "." for cell in row))
        print("\n")

# Example usage
if __name__ == "__main__":
    client = Game2048Client()
    client.start_game()

    # Create a list of moves
    moves = ["UP", "LEFT", "DOWN", "RIGHT"]

    # Run a random move until game over or state does not change
    while True:
        # Get current game state
        state = client.get_state()
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

        # Make a random move
        move = random.choice(moves)
        result = client.make_move(move)

        # If move failed, exit
        if result is None:
            print("Failed to make a move. Exiting.")
            break