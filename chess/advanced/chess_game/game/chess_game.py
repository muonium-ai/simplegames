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
        self.move_count = 0
        self.last_move = None
        self.captured_white = []
        self.captured_black = []
        self.check_status = ''
        self.castling_occurred = False

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
                    move = self.white_player.make_move(self.board)
                    if move:
                        self.board.push(move)
                        self.update_game_state(move)
            else:
                if self.black_player:
                    move = self.black_player.make_move(self.board)
                    if move:
                        self.board.push(move)
                        self.update_game_state(move)

            # Draw the board and update the display
            self.gui.draw_board(self.board)
            pygame.display.flip()
            clock.tick(30)  # Limit to 30 frames per second to reduce CPU usage

        pygame.quit()

    def update_game_state(self, move):
        self.move_count += 1
        self.last_move = move.uci()

        # Update captured pieces
        if self.board.is_capture(move):
            captured_square = move.to_square
            captured_piece = self.board.piece_at(captured_square)
            if captured_piece:
                piece_symbol = self.gui.UNICODE_PIECES[captured_piece.symbol()]
                if captured_piece.color == chess.WHITE:
                    self.captured_white.append(piece_symbol)
                else:
                    self.captured_black.append(piece_symbol)

        # Check for check or checkmate
        if self.board.is_checkmate():
            self.check_status = 'Checkmate'
        elif self.board.is_check():
            self.check_status = 'Check'
        else:
            self.check_status = ''

        # Check for castling
        if move in [chess.Move.from_uci('e1g1'), chess.Move.from_uci('e1c1'),
                    chess.Move.from_uci('e8g8'), chess.Move.from_uci('e8c8')]:
            self.castling_occurred = True
        else:
            self.castling_occurred = False

        # Update GUI with new game state
        self.gui.update_game_state(
            self.move_count,
            self.last_move,
            self.captured_white,
            self.captured_black,
            self.check_status,
            self.castling_occurred
        )