# server.py
import threading
import uuid
import io
from flask import Flask, jsonify, request, send_file
from game_2048.game import Game2048
from game_2048.gui import GameGUI, TextRenderer
from game_2048.constants import *
import pygame

class ServerGame(Game2048):
    def __init__(self):
        super().__init__()
        self.game_id = str(uuid.uuid4())
        self.game_won = False
        self.game_over = False

    def reset(self):
        super().__init__()
        self.game_id = str(uuid.uuid4())
        self.game_won = False
        self.game_over = False

    def get_state_dict(self):
        status = "won" if self.game_won else "over" if self.game_over else "ongoing"
        return {
            "game_id": self.game_id,
            "state": self.grid,
            "score": self.score,
            "total_moves": self.total_moves,
            "max_tile": self.max_tile,
            "status": status
        }

class ServerGUI(GameGUI):
    def __init__(self, server_game):
        pygame.init()
        self.window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('2048 Extended Server')
        self.clock = pygame.time.Clock()
        self.game = server_game
        
        # Calculate grid measurements
        self.grid_padding = 10
        self.grid_top = 100
        self.tile_size = (WINDOW_WIDTH - (self.grid_padding * 5)) // GAME_SIZE
        self.grid_size = self.tile_size * GAME_SIZE + self.grid_padding * (GAME_SIZE + 1)

    def reset_screen(self):
        self.window.fill(BACKGROUND)
        TextRenderer.draw_text(
            self.window,
            f"Game ID: {self.game.game_id}",
            36,
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            TEXT_DARK
        )
        pygame.display.update()

    def capture_screenshot(self):
        if pygame.display.get_surface():
            img_bytes = io.BytesIO()
            pygame.image.save(pygame.display.get_surface(), img_bytes, "PNG")
            img_bytes.seek(0)
            return img_bytes
        return None

class FlaskServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.game = ServerGame()
        self.gui = ServerGUI(self.game)
        self.setup_routes()
        self._running = True

    def setup_routes(self):
        @self.app.route('/start', methods=['POST'])
        def start_game():
            self.game.reset()
            self.gui.reset_screen()
            return jsonify(self.game.get_state_dict()), 201

        @self.app.route('/move', methods=['POST'])
        def make_move():
            direction = request.json.get("direction")
            if direction not in ["UP", "DOWN", "LEFT", "RIGHT"]:
                return jsonify({"error": "Invalid move direction"}), 400

            moved = self.game.move(direction)
            if moved:
                self.gui.draw()
            return jsonify({**self.game.get_state_dict(), "moved": moved})

        @self.app.route('/state', methods=['GET'])
        def get_state():
            return jsonify(self.game.get_state_dict())

        @self.app.route('/screenshot', methods=['GET'])
        def screenshot():
            img_bytes = self.gui.capture_screenshot()
            if img_bytes:
                return send_file(img_bytes, mimetype='image/png')
            return jsonify({"error": "Screenshot failed"}), 500

    def run(self):
        # Start Flask in a separate thread
        flask_thread = threading.Thread(
            target=lambda: self.app.run(debug=False, use_reloader=False)
        )
        flask_thread.daemon = True
        flask_thread.start()

        # Main game loop
        try:
            self.gui.reset_screen()
            while self._running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self._running = False

                self.gui.draw()
                self.gui.clock.tick(60)
        except Exception as e:
            print(f"Error in game loop: {e}")
        finally:
            pygame.quit()

def main():
    server = FlaskServer()
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Server error: {e}")

if __name__ == "__main__":
    main()