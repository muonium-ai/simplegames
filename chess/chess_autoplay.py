import pygame
import chess
import random
import sys

# Initialize Pygame
pygame.init()
screen_width = 520
screen_height = 560
square_size = 60
label_offset = 20
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Chess Game - You Play Black")

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

# Board labels (from Black's perspective)
COLUMNS = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8']

def draw_board(board, selected_square=None):
    """Draw the chessboard with labels, pieces, and highlights."""
    screen.fill((255, 255, 255))

    # Draw squares and pieces
    for row in range(8):
        for col in range(8):
            actual_col = 7 - col  # Adjust for Black's perspective
            actual_row = row
            square = chess.square(actual_col, actual_row)
            
            # Determine square color
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            
            # Highlight selected square
            if selected_square is not None and square == selected_square:
                color = HIGHLIGHT_COLOR
            
            # Draw square
            pygame.draw.rect(
                screen, 
                color, 
                pygame.Rect(col * square_size + label_offset, 
                          row * square_size + label_offset, 
                          square_size, square_size)
            )

            # Draw piece
            piece = board.piece_at(square)
            if piece:
                piece_symbol = UNICODE_PIECES[piece.symbol()]
                # Changed: Swap the colors - white pieces are now WHITE_PIECE_COLOR
                piece_color = WHITE_PIECE_COLOR if piece.color == chess.WHITE else BLACK_PIECE_COLOR
                text_surface = font.render(piece_symbol, True, piece_color)
                text_rect = text_surface.get_rect(
                    center=(col * square_size + label_offset + square_size // 2,
                           row * square_size + label_offset + square_size // 2))
                screen.blit(text_surface, text_rect)

    # Draw labels
    for i in range(8):
        # Column labels
        col_label = label_font.render(COLUMNS[i], True, LABEL_COLOR)
        screen.blit(col_label, (i * square_size + label_offset + square_size // 2 - 
                               col_label.get_width() // 2, label_offset // 2))
        screen.blit(col_label, (i * square_size + label_offset + square_size // 2 - 
                               col_label.get_width() // 2, screen_height - label_offset))

        # Row labels
        row_label = label_font.render(ROWS[i], True, LABEL_COLOR)
        screen.blit(row_label, (label_offset // 2, 
                               i * square_size + label_offset + square_size // 2 - 
                               row_label.get_height() // 2))
        screen.blit(row_label, (screen_width - label_offset // 2 - row_label.get_width(),
                               i * square_size + label_offset + square_size // 2 - 
                               row_label.get_height() // 2))

    pygame.display.flip()

def get_square_from_mouse(pos):
    """Convert mouse position to chess square."""
    x, y = pos
    if label_offset <= x < screen_width - label_offset and \
       label_offset <= y < screen_height - label_offset:
        col = (x - label_offset) // square_size
        row = (y - label_offset) // square_size
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(7 - col, row)  # Adjust for Black's perspective
    return None

def make_computer_move(board):
    """Make a random legal move for the computer (White)."""
    legal_moves = list(board.legal_moves)
    if legal_moves:
        move = random.choice(legal_moves)
        board.push(move)
        return True
    return False

def display_game_over(board):
    """Display game over message."""
    screen.fill((255, 255, 255))
    if board.is_checkmate():
        winner = "White wins!" if board.turn == chess.BLACK else "Black wins!"
    elif board.is_stalemate():
        winner = "Draw by stalemate!"
    elif board.is_insufficient_material():
        winner = "Draw by insufficient material!"
    else:
        winner = "Game Over!"
    
    text_surface = font.render(winner, True, (0, 0, 0))
    text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text_surface, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)

def main():
    board = chess.Board()
    selected_square = None
    
    # Computer (White) makes the first move
    make_computer_move(board)
    draw_board(board)

    while not board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and board.turn == chess.BLACK:
                clicked_square = get_square_from_mouse(event.pos)
                
                if clicked_square is not None:
                    if selected_square is None:
                        # Select piece if it's valid
                        piece = board.piece_at(clicked_square)
                        if piece and piece.color == chess.BLACK:
                            selected_square = clicked_square
                            draw_board(board, selected_square)
                    else:
                        # Try to make a move
                        move = chess.Move(selected_square, clicked_square)
                        if move in board.legal_moves:
                            board.push(move)
                            selected_square = None
                            draw_board(board)

                            # Computer's turn
                            if not board.is_game_over():
                                pygame.time.wait(500)  # Slight delay before computer moves
                                make_computer_move(board)
                                draw_board(board)
                        else:
                            # If invalid move, check if new square selection
                            piece = board.piece_at(clicked_square)
                            selected_square = clicked_square if piece and piece.color == chess.BLACK else None
                            draw_board(board, selected_square)

    display_game_over(board)

if __name__ == "__main__":
    main()