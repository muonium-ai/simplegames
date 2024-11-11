# game/chess_game.py

import pygame
import chess
from .player import Player
from .random_computer_player import RandomComputerPlayer
from .minimax_computer_player import MinimaxComputerPlayer
from .minimax_computer_player2 import MinimaxComputerPlayer2
from .minimax_computer_player3 import MinimaxComputerPlayer3
from ..gui.chess_gui import ChessGUI

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
            # Handle events (for computer-only game, minimal events handling)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Check if the game is over
            if self.board.is_game_over():
                print("Game over!")
                print(f"Result: {self.board.result()}")
                self.running = False
                continue

            # Let computer players make moves
            if self.board.turn == chess.WHITE and self.white_player:
                move = self.white_player.make_move(self.board)
                if move:
                    # Capture piece before making the move
                    captured_piece = self.get_captured_piece(move)
                    if captured_piece:
                        piece_symbol = self.gui.UNICODE_PIECES.get(captured_piece.symbol(), '')
                        if piece_symbol:
                            if captured_piece.color == chess.WHITE:
                                self.captured_white.append(piece_symbol)
                            else:
                                self.captured_black.append(piece_symbol)
                    self.board.push(move)
                    self.update_game_state(move)
            elif self.board.turn == chess.BLACK and self.black_player:
                move = self.black_player.make_move(self.board)
                if move:
                    # Capture piece before making the move
                    captured_piece = self.get_captured_piece(move)
                    if captured_piece:
                        piece_symbol = self.gui.UNICODE_PIECES.get(captured_piece.symbol(), '')
                        if piece_symbol:
                            if captured_piece.color == chess.WHITE:
                                self.captured_white.append(piece_symbol)
                            else:
                                self.captured_black.append(piece_symbol)
                    self.board.push(move)
                    self.update_game_state(move)

            # Draw the board and update the display
            self.gui.draw_board(self.board)
            pygame.display.flip()
            clock.tick(2)  # Adjust FPS as needed

        pygame.quit()

    def get_captured_piece(self, move: chess.Move):
        """Retrieve the captured piece based on the move."""
        if not self.board.is_capture(move):
            return None

        if self.board.is_en_passant(move):
            # For en passant, the captured pawn is not on the to_square
            direction = 1 if self.board.turn == chess.WHITE else -1
            captured_square = chess.square(
                file=chess.square_file(move.to_square),
                rank=chess.square_rank(move.to_square) - direction
            )
        else:
            # Otherwise, the captured piece is on the to_square
            captured_square = move.to_square

        return self.board.piece_at(captured_square)

    def update_game_state(self, move: chess.Move):
        """Update the game state information after a move."""
        self.move_count += 1
        self.last_move = move.uci()

        # Check for check or checkmate
        if self.board.is_checkmate():
            self.check_status = 'Checkmate'
        elif self.board.is_check():
            self.check_status = 'Check'
        else:
            self.check_status = ''

        # Check for castling
        if move in [
            chess.Move.from_uci('e1g1'), chess.Move.from_uci('e1c1'),
            chess.Move.from_uci('e8g8'), chess.Move.from_uci('e8c8')
        ]:
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