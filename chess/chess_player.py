import pygame
import chess
import chess.pgn
import sys

# Initialize Pygame
pygame.init()
screen_size = 400  # Size of the chessboard in pixels
square_size = screen_size // 8
screen = pygame.display.set_mode((screen_size, screen_size))
pygame.display.set_caption("Chess Replay")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
light_square = (240, 217, 181)
dark_square = (181, 136, 99)

# Load PGN from file
pgn_file = sys.argv[1] if len(sys.argv) > 1 else "game.pgn"
with open(pgn_file) as f:
    game = chess.pgn.read_game(f)

# Initialize the board
board = game.board()

# Setup game variables
clock = pygame.time.Clock()
moves = list(game.mainline_moves())
move_index = 0
move_time = 1000  # 1 second in milliseconds

# Piece font
pygame.font.init()
font = pygame.font.SysFont('Arial', square_size // 2)

# Function to draw board and pieces
def draw_board(board):
    for row in range(8):
        for col in range(8):
            # Alternate colors for the squares
            color = light_square if (row + col) % 2 == 0 else dark_square
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size, square_size, square_size))
            
            # Draw pieces
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_text = piece.symbol().upper() if piece.color == chess.WHITE else piece.symbol().lower()
                text_surface = font.render(piece_text, True, black if piece.color == chess.WHITE else white)
                screen.blit(text_surface, (col * square_size + square_size // 4, row * square_size + square_size // 4))

    pygame.display.flip()

# Main loop
running = True
last_move_time = pygame.time.get_ticks()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks()
    
    # Display the next move every second
    if move_index < len(moves) and current_time - last_move_time >= move_time:
        board.push(moves[move_index])
        draw_board(board)
        move_index += 1
        last_move_time = current_time

    clock.tick(30)  # Run at 30 FPS

pygame.quit()
