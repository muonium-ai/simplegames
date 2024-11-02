import requests
import os
import time
import random
from datetime import datetime

class Game2048Client:
    def __init__(self, server_url="http://127.0.0.1:5000", depth=3):
        self.server_url = server_url
        self.game_id = None
        self.screenshot_count = 0
        self.screenshot_folder = "screenshots"
        self.depth = depth  # Maximum depth for MCTS

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

    def simulate_move(self, grid, move):
        """Simulates a move by sending it to the server and returns the resulting state."""
        # Temporary function for server simulation - assumes the server implements a similar move function
        simulated_response = self.make_move(move)
        return simulated_response

    def monte_carlo_tree_search(self, grid):
        """Uses MCTS to decide the best move."""
        move_priority = ["DOWN", "RIGHT", "LEFT", "UP"]
        move_scores = {move: 0 for move in move_priority}

        for move in move_priority:
            total_score = 0
            for _ in range(self.depth):
                simulated_response = self.simulate_move(grid, move)
                if simulated_response and simulated_response["moved"]:
                    total_score += self.get_max_tile(simulated_response["state"])
            move_scores[move] = total_score / self.depth if self.depth > 0 else 0

        # Choose the move with the highest average score from simulations
        best_move = max(move_scores, key=move_scores.get)
        print(f"Best Move (MCTS): {best_move} | Average Score: {move_scores[best_move]}")
        return best_move

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

            # Use MCTS to select the best move
            best_move = self.monte_carlo_tree_search(state["state"])
            if best_move:
                self.make_move(best_move)
                time.sleep(0.1)  # Small delay to avoid rapid requests

# Example usage
if __name__ == "__main__":
    client = Game2048Client(depth=50)  # Define the depth as needed
    # Run the game 25 times
    for i in range(25):
        client.start_game()
        client.solve()
        print(f"Game {i + 1} completed")
