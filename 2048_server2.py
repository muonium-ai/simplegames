import pygame
import random
from flask import Flask, jsonify, request
import uuid
import threading
import signal
import sys
import time

# Pygame setup
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500
GAME_SIZE = 4
BACKGROUND = (187, 173, 160)
EMPTY_CELL = (205, 193, 180)
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46)
}
TEXT_DARK = (119, 110, 101)
TEXT_LIGHT = (249, 246, 242)

# Flask setup
app = Flask(__name__)
shutdown_flag = False

# Game class (unchanged)
class Game:
    def __init__(self):
        self.grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        self.score = 0
        self.game_id = str(uuid.uuid4())
        self.add_new_tile()
        self.add_new_tile()
        self.game_won = False
        self.game_over = False

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(GAME_SIZE) for j in range(GAME_SIZE) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4

    def move(self, direction):
        original_grid = [row[:] for row in self.grid]
        moved = False

        if direction in ['UP', 'DOWN']:
            self.transpose()
        if direction in ['RIGHT', 'DOWN']:
            self.reverse()

        self.compress()
        score_added = self.merge()
        self.compress()

        if direction in ['RIGHT', 'DOWN']:
            self.reverse()
        if direction in ['UP', 'DOWN']:
            self.transpose()

        if original_grid != self.grid:
            moved = True
            self.score += score_added
            self.add_new_tile()

        self.game_over = self.is_game_over()
        self.game_won = self.has_won()
        return moved

    def compress(self):
        new_grid = [[0 for _ in range(GAME_SIZE)] for _ in range(GAME_SIZE)]
        for i in range(GAME_SIZE):
            pos = 0
            for j in range(GAME_SIZE):
                if self.grid[i][j] != 0:
                    new_grid[i][pos] = self.grid[i][j]
                    pos += 1
        self.grid = new_grid

    def merge(self):
        score_added = 0
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE - 1):
                if self.grid[i][j] != 0 and self.grid[i][j] == self.grid[i][j + 1]:
                    self.grid[i][j] *= 2
                    score_added += self.grid[i][j]
                    self.grid[i][j + 1] = 0
        return score_added

    def reverse(self):
        self.grid = [row[::-1] for row in self.grid]

    def transpose(self):
        self.grid = [[self.grid[j][i] for j in range(GAME_SIZE)] for i in range(GAME_SIZE)]

    def is_game_over(self):
        if any(0 in row for row in self.grid):
            return False
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                current = self.grid[i][j]
                if j < GAME_SIZE - 1 and current == self.grid[i][j + 1]:
                    return False
                if i < GAME_SIZE - 1 and current == self.grid[i + 1][j]:
                    return False
        return True

    def has_won(self):
        return any(2048 in row for row in self.grid)

game_instance = Game()

# Flask API endpoints
@app.route('/start', methods=['POST'])
def start_game():
    global game_instance
    game_instance = Game()
    return jsonify({"game_id": game_instance.game_id, "state": game_instance.grid, "score": game_instance.score, "status": "ongoing"}), 201

@app.route('/move', methods=['POST'])
def make_move():
    direction = request.json.get("direction")
    if direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
        return jsonify({"error": "Invalid move direction"}), 400

    moved = game_instance.move(direction)
    status = "won" if game_instance.game_won else "over" if game_instance.game_over else "ongoing"

    return jsonify({
        "game_id": game_instance.game_id,
        "state": game_instance.grid,
        "score": game_instance.score,
        "status": status,
        "moved": moved
    })

@app.route('/state', methods=['GET'])
def get_state():
    status = "won" if game_instance.game_won else "over" if game_instance.game_over else "ongoing"
    return jsonify({
        "game_id": game_instance.game_id,
        "state": game_instance.grid,
        "score": game_instance.score,
        "status": status
    })

# Signal handler
def handle_exit(signal, frame):
    global shutdown_flag
    print("\nExiting game and shutting down server...")
    shutdown_flag = True  # Signal to stop both threads
    pygame.quit()
    sys.exit(0)

# Pygame and Flask threading
def run_flask():
    while not shutdown_flag:
        try:
            app.run(debug=False, use_reloader=False)
        except RuntimeError:
            break  # Exit if server shuts down

def main():
    global shutdown_flag
    signal.signal(signal.SIGINT, handle_exit)  # Handle Ctrl+C

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Pygame setup
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('2048')
    clock = pygame.time.Clock()

    while not shutdown_flag:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                handle_exit(None, None)  # Trigger clean exit if window is closed

        # (Your existing game drawing and logic code would go here)
        window.fill(BACKGROUND)  # Example for clearing the screen
        pygame.display.update()
        clock.tick(60)

    print("Server and game exited cleanly.")

if __name__ == "__main__":
    main()
