# chess_game/game/chess_game.py

import pygame
import chess
import sys
from ..gui.chess_gui import ChessGUI
from .chess_player import RandomComputerPlayer

class ChessGame:
    """Main game class that coordinates the GUI, board state, and players."""
    
    def __init__(self, computer_player_class=RandomComputerPlayer):
        self.gui = ChessGUI()
        self.board = chess.Board()
        self.computer = computer_player_class()
        self.selected_square = None

    def run(self):
        """Main game loop."""
        # Computer (White) makes the first move
        self.computer.make_move(self.board)
        self.gui.draw_board(self.board)

        while not self.board.is_game_over():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and self.board.turn == chess.BLACK:
                    self._handle_mouse_click(event.pos)

        self.gui.display_game_over(self.board)

    def _handle_mouse_click(self, pos):
        """Handle mouse click events for the human player."""
        clicked_square = self.gui.get_square_from_mouse(pos)
        
        if clicked_square is not None:
            if self.selected_square is None:
                # Select piece if it's valid
                piece = self.board.piece_at(clicked_square)
                if piece and piece.color == chess.BLACK:
                    self.selected_square = clicked_square
                    self.gui.draw_board(self.board, self.selected_square)
            else:
                # Try to make a move
                move = chess.Move(self.selected_square, clicked_square)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.selected_square = None
                    self.gui.draw_board(self.board)

                    # Computer's turn
                    if not self.board.is_game_over():
                        pygame.time.wait(500)  # Slight delay before computer moves
                        self.computer.make_move(self.board)
                        self.gui.draw_board(self.board)
                else:
                    # If invalid move, check if new square selection
                    piece = self.board.piece_at(clicked_square)
                    self.selected_square = clicked_square if piece and piece.color == chess.BLACK else None
                    self.gui.draw_board(self.board, self.selected_square)