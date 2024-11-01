import pygame
import random
from flask import Flask, jsonify, request
import uuid
import threading

# Pygame Window setup
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

app = Flask(__name__)

# Game class
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

# API Endpoints
game_instance = Game()

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

# Run Flask in a separate thread
def run_flask():
    app.run(debug=True, use_reloader=False)

# Pygame display functions
def draw_text(window, text, font_size, x, y, color):
    font = pygame.font.SysFont('Arial', font_size, bold=True)
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    window.blit(text_surface, text_rect)

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('2048')
    clock = pygame.time.Clock()

    threading.Thread(target=run_flask).start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and not game_instance.game_over:
                if event.key == pygame.K_UP:
                    game_instance.move('UP')
                elif event.key == pygame.K_DOWN:
                    game_instance.move('DOWN')
                elif event.key == pygame.K_LEFT:
                    game_instance.move('LEFT')
                elif event.key == pygame.K_RIGHT:
                    game_instance.move('RIGHT')

        # Draw background
        window.fill(BACKGROUND)
        pygame.draw.rect(window, EMPTY_CELL, (10, 10, WINDOW_WIDTH - 20, 60), border_radius=5)
        draw_text(window, f"Score: {game_instance.score}", 32, WINDOW_WIDTH // 2, 40, TEXT_DARK)

        # Draw grid
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                x = j * (WINDOW_WIDTH // GAME_SIZE)
                y = i * (WINDOW_WIDTH // GAME_SIZE) + 100
                value = game_instance.grid[i][j]
                pygame.draw.rect(window, TILE_COLORS.get(value, EMPTY_CELL), (x + 5, y + 5, WINDOW_WIDTH // GAME_SIZE - 10, WINDOW_WIDTH // GAME_SIZE - 10), border_radius=5)
                if value != 0:
                    font_size = 48 if value < 100 else 36 if value < 1000 else 24
                    text_color = TEXT_DARK if value <= 4 else TEXT_LIGHT
                    draw_text(window, value, font_size, x + WINDOW_WIDTH // GAME_SIZE // 2, y + WINDOW_WIDTH // GAME_SIZE // 2, text_color)

        if game_instance.game_over:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(128)
            window.blit(overlay, (0, 0))
            draw_text(window, "Game Over!", 64, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, TEXT_LIGHT)
        elif game_instance.game_won:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.fill((255, 223, 0))
            overlay.set_alpha(128)
            window.blit(overlay, (0, 0))
            draw_text(window, "You Win!", 64, WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, TEXT_DARK)

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
