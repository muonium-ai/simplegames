# gui/chess_gui.py

import pygame
import chess

class ChessGUI:
    def __init__(self):
        # Initialize Pygame and screen variables
        self.screen_width = 520
        self.screen_height = 600  # Increased height for menu
        self.square_size = 60
        self.label_offset = 20
        self.menu_height = 80  # Height for the menu bar
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Chess Game")
        
        # Colors
        self.LIGHT_SQUARE = (240, 217, 181)
        self.DARK_SQUARE = (181, 136, 99)
        self.HIGHLIGHT_COLOR = (186, 202, 68)
        self.LABEL_COLOR = (0, 0, 0)
        self.WHITE_PIECE_COLOR = (255, 255, 255)
        self.BLACK_PIECE_COLOR = (0, 0, 0)
        self.MENU_BG_COLOR = (200, 200, 200)
        
        # Fonts
        self.font = pygame.font.SysFont("Segoe UI Symbol", self.square_size - 10)
        self.label_font = pygame.font.SysFont("Arial", 20)
        self.menu_font = pygame.font.SysFont("Arial", 18)
        
        # Unicode pieces as an instance attribute
        self.UNICODE_PIECES = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖',
            'Q': '♕', 'K': '♔', 'p': '♟', 'n': '♞',
            'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
        }
        
        # Game state tracking
        self.move_count = 0
        self.last_move = None
        self.captured_white = []
        self.captured_black = []
        self.check_status = ''
        self.castling_occurred = False

    def draw_menu(self, board):
        # Draw menu background
        pygame.draw.rect(self.screen, self.MENU_BG_COLOR, (0, 0, self.screen_width, self.menu_height))
        
        # Move count
        move_text = self.menu_font.render(f"Move: {self.move_count}", True, self.LABEL_COLOR)
        self.screen.blit(move_text, (10, 10))
        
        # Last move
        last_move_text = self.menu_font.render(f"Last Move: {self.last_move}", True, self.LABEL_COLOR)
        self.screen.blit(last_move_text, (10, 30))
        
        # Captured pieces
        captured_white_text = self.menu_font.render("White Captured: " + ''.join(self.captured_white), True, self.LABEL_COLOR)
        self.screen.blit(captured_white_text, (200, 10))
        
        captured_black_text = self.menu_font.render("Black Captured: " + ''.join(self.captured_black), True, self.LABEL_COLOR)
        self.screen.blit(captured_black_text, (200, 30))
        
        # Check status
        check_text = self.menu_font.render(f"Status: {self.check_status}", True, self.LABEL_COLOR)
        self.screen.blit(check_text, (10, 50))
        
        # Castling indication
        if self.castling_occurred:
            castling_text = self.menu_font.render("Castling occurred", True, self.LABEL_COLOR)
            self.screen.blit(castling_text, (200, 50))

    def draw_board(self, board, selected_square=None):
        """Draw the chessboard with labels, pieces, and highlights."""
        # Clear the screen
        self.screen.fill((255, 255, 255))
        
        # Draw the menu
        self.draw_menu(board)
        
        # Adjust board drawing to start below the menu
        board_offset = self.menu_height + self.label_offset
        
        # Draw squares and pieces
        for row in range(8):
            for col in range(8):
                square = chess.square(col, 7 - row)

                # Determine square color
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE
                rect = pygame.Rect(
                    col * self.square_size + self.label_offset,
                    row * self.square_size + board_offset,
                    self.square_size, self.square_size)

                # Draw square
                pygame.draw.rect(self.screen, color, rect)

                # Highlight selected square
                if selected_square == square:
                    pygame.draw.rect(self.screen, self.HIGHLIGHT_COLOR, rect)

                # Draw pieces
                piece = board.piece_at(square)
                if piece:
                    piece_symbol = self.UNICODE_PIECES[piece.symbol()]
                    piece_color = self.WHITE_PIECE_COLOR if piece.color == chess.WHITE else self.BLACK_PIECE_COLOR
                    text_surface = self.font.render(piece_symbol, True, piece_color)
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)

        # Optionally, draw labels (ranks and files)
        self.draw_labels()

    def draw_labels(self):
        """Draw the labels for ranks and files."""
        # Draw file labels (a to h)
        for col in range(8):
            file_label = self.label_font.render(chr(ord('a') + col), True, self.LABEL_COLOR)
            self.screen.blit(file_label, (
                col * self.square_size + self.label_offset + self.square_size / 2 - file_label.get_width() / 2,
                self.menu_height + 8 * self.square_size + self.label_offset + 5))
        
        # Draw rank labels (1 to 8)
        for row in range(8):
            rank_label = self.label_font.render(str(row + 1), True, self.LABEL_COLOR)
            self.screen.blit(rank_label, (
                self.label_offset - 15,
                self.menu_height + row * self.square_size + self.square_size / 2 - rank_label.get_height() / 2))

    def update_game_state(self, move_count, last_move, captured_white, captured_black, check_status, castling_occurred):
        """Update the game state information for the menu."""
        self.move_count = move_count
        self.last_move = last_move
        self.captured_white = captured_white
        self.captured_black = captured_black
        self.check_status = check_status
        self.castling_occurred = castling_occurred