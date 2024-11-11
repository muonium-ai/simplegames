import pygame
import chess
import random

# Initialize Pygame
pygame.init()
screen_size = 480
square_size = screen_size // 8
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Chess with Random Move Player")

# Colors and fonts
light_square = (240, 217, 181)
dark_square = (181, 136, 99)
font = pygame.font.SysFont("Segoe UI Symbol", square_size - 10)

# Initialize the chess board
board = chess.Board()

# Unicode pieces dictionary
unicode_pieces = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # White pieces
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'   # Black pieces
}

def draw_board():
    """Draw the chessboard and pieces."""
    for row in range(8):
        for col in range(8):
            color = light_square if (row + col) % 2 == 0 else dark_square
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))

            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_symbol = unicode_pieces[piece.symbol()]
                text_surface = font.render(piece_symbol, True, (0, 0, 0) if piece.color == chess.WHITE else (255, 255, 255))
                text_rect = text_surface.get_rect(center=(col * square_size + square_size // 2, row * square_size + square_size // 2))
                screen.blit(text_surface, text_rect)

    pygame.display.flip()

def random_move():
    """Make a random legal move for the computer."""
    legal_moves = list(board.legal_moves)
    if legal_moves:
        move = random.choice(legal_moves)
        board.push(move)
        draw_board()

def handle_player_move(move):
    """Handle the player move, update board, and trigger random computer move."""
    if board.is_legal(move):
        board.push(move)
        draw_board()
        # Trigger computer's random move after the player move
        random_move()

def main():
    draw_board()
    selected_square = None

    while not board.is_game_over():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            elif event.type == pygame.MOUSEBUTTONDOWN:
                col = event.pos[0] // square_size
                row = 7 - (event.pos[1] // square_size)
                square = chess.square(col, row)

                if selected_square is None:
                    # Select a piece to move
                    piece = board.piece_at(square)
                    if piece and piece.color == board.turn:
                        selected_square = square
                else:
                    # Attempt to move the selected piece
                    move = chess.Move(selected_square, square)
                    if move in board.legal_moves:
                        handle_player_move(move)
                    selected_square = None

        pygame.display.update()

    # Show game over result
    result_text = "Draw" if board.is_stalemate() else "Checkmate!"
    text_surface = font.render(result_text, True, (0, 0, 0))
    screen.blit(text_surface, (screen_size // 2 - text_surface.get_width() // 2, screen_size // 2))
    pygame.display.update()
    pygame.time.wait(3000)

if __name__ == "__main__":
    main()
