# chess_game/gui/chess_gui.py

import pygame
import chess

from chess.advanced.config import LABEL_OFFSET, SCREEN_HEIGHT, SCREEN_WIDTH, SQUARE_SIZE

#from chess.chess_autoplay import BLACK_PIECE_COLOR, COLUMNS, DARK_SQUARE, HIGHLIGHT_COLOR, LABEL_COLOR, LIGHT_SQUARE, ROWS, UNICODE_PIECES, WHITE_PIECE_COLOR

screen_width = 520
screen_height = 560
square_size = 60
label_offset = 20
screen = pygame.display.set_mode((screen_width, screen_height))

# Colors and fonts
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
LABEL_COLOR = (0, 0, 0)
WHITE_PIECE_COLOR = (255, 255, 255)  # Changed: White pieces will render as white
BLACK_PIECE_COLOR = (0, 0, 0)        # Changed: Black pieces will render as black
font = pygame.font.SysFont("Segoe UI Symbol", square_size - 10)
label_font = pygame.font.SysFont("Arial", 20)

# Unicode pieces dictionary
UNICODE_PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}


# Board labels
COLUMNS = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8']


from ..config import *

class ChessGUI:
    """Handles the graphical interface and game display."""
    
    def __init__(self):
        # Initialize Pygame and create window
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chess Game - You Play Black")
        
        # Fonts
        self.piece_font = pygame.font.SysFont("Segoe UI Symbol", SQUARE_SIZE - 10)
        self.label_font = pygame.font.SysFont("Arial", 20)

    def draw_board(self, board, selected_square=None):
        """Draw the chessboard with labels, pieces, and highlights."""
        self.screen.fill((255, 255, 255))

        # Draw squares and pieces
        for row in range(8):
            for col in range(8):
                actual_col = 7 - col
                actual_row = row
                square = chess.square(actual_col, actual_row)
                
                # Determine square color
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                if selected_square is not None and square == selected_square:
                    color = HIGHLIGHT_COLOR
                
                # Draw square
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    pygame.Rect(
                        col * SQUARE_SIZE + LABEL_OFFSET,
                        row * SQUARE_SIZE + LABEL_OFFSET,
                        SQUARE_SIZE,
                        SQUARE_SIZE
                    )
                )

                # Draw piece
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = UNICODE_PIECES[piece.symbol()]
                    piece_color = WHITE_PIECE_COLOR if piece.color == chess.WHITE else BLACK_PIECE_COLOR
                    text_surface = self.piece_font.render(piece_symbol, True, piece_color)
                    text_rect = text_surface.get_rect(
                        center=(
                            col * SQUARE_SIZE + LABEL_OFFSET + SQUARE_SIZE // 2,
                            row * SQUARE_SIZE + LABEL_OFFSET + SQUARE_SIZE // 2
                        )
                    )
                    self.screen.blit(text_surface, text_rect)

        self._draw_labels()
        pygame.display.flip()

    def _draw_labels(self):
        """Draw the board labels."""
        for i in range(8):
            # Column labels
            col_label = self.label_font.render(COLUMNS[i], True, LABEL_COLOR)
            self.screen.blit(
                col_label,
                (i * SQUARE_SIZE + LABEL_OFFSET + SQUARE_SIZE // 2 - col_label.get_width() // 2,
                 LABEL_OFFSET // 2)
            )
            self.screen.blit(
                col_label,
                (i * SQUARE_SIZE + LABEL_OFFSET + SQUARE_SIZE // 2 - col_label.get_width() // 2,
                 SCREEN_HEIGHT - LABEL_OFFSET)
            )

            # Row labels
            row_label = self.label_font.render(ROWS[i], True, LABEL_COLOR)
            self.screen.blit(
                row_label,
                (LABEL_OFFSET // 2,
                 i * SQUARE_SIZE + LABEL_OFFSET + SQUARE_SIZE // 2 - row_label.get_height() // 2)
            )
            self.screen.blit(
                row_label,
                (SCREEN_WIDTH - LABEL_OFFSET // 2 - row_label.get_width(),
                 i * SQUARE_SIZE + LABEL_OFFSET + SQUARE_SIZE // 2 - row_label.get_height() // 2)
            )

    def get_square_from_mouse(self, pos):
        """Convert mouse position to chess square."""
        x, y = pos
        if (LABEL_OFFSET <= x < SCREEN_WIDTH - LABEL_OFFSET and
            LABEL_OFFSET <= y < SCREEN_HEIGHT - LABEL_OFFSET):
            col = (x - LABEL_OFFSET) // SQUARE_SIZE
            row = (y - LABEL_OFFSET) // SQUARE_SIZE
            if 0 <= col < 8 and 0 <= row < 8:
                return chess.square(7 - col, row)
        return None

    def display_game_over(self, board):
        """Display game over message."""
        self.screen.fill((255, 255, 255))
        if board.is_checkmate():
            winner = "White wins!" if board.turn == chess.BLACK else "Black wins!"
        elif board.is_stalemate():
            winner = "Draw by stalemate!"
        elif board.is_insufficient_material():
            winner = "Draw by insufficient material!"
        else:
            winner = "Game Over!"
        
        text_surface = self.piece_font.render(winner, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)
        pygame.display.flip()
        pygame.time.wait(3000)