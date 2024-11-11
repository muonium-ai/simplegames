# game/chess_game.py

import pygame
import chess
from ..gui.chess_gui import ChessGUI
from .chess_player import RandomComputerPlayer

class ChessGame:
    """Main game class that coordinates the GUI, board state, and players."""
    
    def __init__(self, white_player_class=None, black_player_class=None):
        pygame.init()
        self.gui = ChessGUI()
        self.board = chess.Board()
        self.white_player = white_player_class() if white_player_class else None
        self.black_player = black_player_class() if black_player_class else None
        self.running = True

    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # If the game is over, break the loop
            if self.board.is_game_over():
                print("Game over!")
                print(f"Result: {self.board.result()}")
                self.running = False
                continue

            # Determine whose turn it is
            if self.board.turn == chess.WHITE:
                if self.white_player:
                    move = self.white_player.make_move(self.board)  # Changed to make_move
                    if move:
                        self.board.push(move)
            else:
                if self.black_player:
                    move = self.black_player.make_move(self.board)  # Changed to make_move
                    if move:
                        self.board.push(move)

            # Draw the board and update the display
            self.gui.draw_board(self.board)
            pygame.display.flip()
            clock.tick(30)  # Limit to 30 frames per second to reduce CPU usage

        pygame.quit()