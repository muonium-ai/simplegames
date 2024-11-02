import requests
import os
import time
import random
import math
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
            max_tile = self.get_max_tile(data["state"])  # Get max tile after the move
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

    def empty_tile_heuristic(self, grid):
        return sum(row.count(0) for row in grid)

    def smoothness_heuristic(self, grid):
        smoothness = 0
        for x in range(4):
            for y in range(4):
                if grid[x][y]:
                    value = math.log2(grid[x][y])
                    for direction in [(1, 0), (0, 1)]:  # Right and down
                        dx, dy = direction
                        nx, ny = x + dx, y + dy
                        while 0 <= nx < 4 and 0 <= ny < 4:
                            if grid[nx][ny]:
                                target_value = math.log2(grid[nx][ny])
                                smoothness -= abs(value - target_value)
                                break
                            nx += dx
                            ny += dy
        return smoothness

    def monotonicity_heuristic(self, grid):
        totals = [0, 0, 0, 0]  # up, down, left, right
        for x in range(4):
            current_row = grid[x]
            for i in range(3):
                current = math.log2(current_row[i]) if current_row[i] else 0
                next = math.log2(current_row[i + 1]) if current_row[i + 1] else 0
                if current > next:
                    totals[0] += next - current
                elif next > current:
                    totals[1] += current - next

        for y in range(4):
            current_column = [grid[x][y] for x in range(4)]
            for i in range(3):
                current = math.log2(current_column[i]) if current_column[i] else 0
                next = math.log2(current_column[i + 1]) if current_column[i + 1] else 0
                if current > next:
                    totals[2] += next - current
                elif next > current:
                    totals[3] += current - next
        return max(totals[0], totals[1]) + max(totals[2], totals[3])

    def max_tile_heuristic(self, grid):
        return math.log2(max(max(row) for row in grid)) if max(max(row) for row in grid) else 0

    def combined_heuristic(self, grid):
        empty_weight = 2.7
        max_tile_weight = 1.0
        smoothness_weight = 0.1
        monotonicity_weight = 1.0
        return (empty_weight * self.empty_tile_heuristic(grid) +
                max_tile_weight * self.max_tile_heuristic(grid) +
                smoothness_weight * self.smoothness_heuristic(grid) +
                monotonicity_weight * self.monotonicity_heuristic(grid))

    def expectimax(self, grid, depth, player_turn, max_depth=3):
        if depth == max_depth or self.get_state()["status"] == "over":
            return self.combined_heuristic(grid), None

        if player_turn:
            max_score = -float('inf')
            best_direction = None
            for direction in ["UP", "DOWN", "LEFT", "RIGHT"]:
                response = self.make_move(direction)
                if response is not None and response["moved"]:
                    score, _ = self.expectimax(response["state"], depth + 1, False, max_depth)
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
                tile_score, _ = self.expectimax(grid, depth + 1, True, max_depth)
                score += 0.9 * tile_score
                grid[r][c] = 4
                tile_score, _ = self.expectimax(grid, depth + 1, True, max_depth)
                score += 0.1 * tile_score
                grid[r][c] = 0  # Reset to empty
            return score / len(empty_cells), None

    def solve(self):
        while True:
            state = self.get_state()
            if state["status"] == "over":
                print("Game Over!")
                break
            elif state["status"] == "won":
                print("Congratulations! You've won the game!")
                break
            _, best_move = self.expectimax(state["state"], 0, True)
            if best_move:
                self.make_move(best_move)
                time.sleep(0.1)

if __name__ == "__main__":
    client = Game2048Client()
    client.start_game()
    client.solve()
