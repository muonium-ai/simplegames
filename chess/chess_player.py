import pygame
import chess
import chess.pgn
import sys
import os

# Initialize Pygame
pygame.init()
screen_size = 800  # Doubled the screen size to 800x800 pixels
square_size = screen_size // 8
info_height = 100  # Increased space above the board for displaying FEN and step information
screen = pygame.display.set_mode((screen_size, screen_size + info_height))
pygame.display.set_caption("Chess Replay")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
light_square = (222, 184, 135)  # A darker shade of beige for better contrast
dark_square = (181, 136, 99)

# Unicode chess pieces
unicode_pieces = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # White pieces
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'   # Black pieces
}

# Load PGN from file
pgn_file = sys.argv[1] if len(sys.argv) > 1 else "game.pgn"
game_name = os.path.splitext(os.path.basename(pgn_file))[0]
screenshot_dir = os.path.join("screenshots", game_name)
os.makedirs(screenshot_dir, exist_ok=True)

with open(pgn_file) as f:
    game = chess.pgn.read_game(f)

# Initialize the board
board = game.board()

# Setup game variables
clock = pygame.time.Clock()
moves = list(game.mainline_moves())
move_index = 0
move_time = 1000  # 1 second in milliseconds

# Fonts
pygame.font.init()
font = pygame.font.SysFont("Segoe UI Symbol", square_size - 10)
info_font = pygame.font.SysFont("Arial", 24)

# Function to draw board and pieces
def draw_board(board, move_index, last_move):
    # Clear the screen
    screen.fill(white)

    # Draw step number, last move, and FEN
    step_text = f"Step: {move_index + 1}"
    last_move_text = f"Last Move: {last_move}" if last_move else "Last Move: -"
    fen_text = f"FEN: {board.fen()}"
    step_surface = info_font.render(step_text, True, black)
    last_move_surface = info_font.render(last_move_text, True, black)
    fen_surface = info_font.render(fen_text, True, black)
    screen.blit(step_surface, (10, 10))
    screen.blit(last_move_surface, (10, 40))
    screen.blit(fen_surface, (10, 70))

    # Draw the chessboard
    for row in range(8):
        for col in range(8):
            # Alternate colors for the squares
            color = light_square if (row + col) % 2 == 0 else dark_square
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size + info_height, square_size, square_size))
            
            # Draw pieces
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_unicode = unicode_pieces[piece.symbol()]
                text_surface = font.render(piece_unicode, True, black if piece.color == chess.WHITE else white)
                
                # Center the piece in the square
                text_rect = text_surface.get_rect(center=(col * square_size + square_size // 2, row * square_size + info_height + square_size // 2))
                screen.blit(text_surface, text_rect)

    pygame.display.flip()

    # Save screenshot of the current step
    screenshot_path = os.path.join(screenshot_dir, f"{move_index + 1:03}.png")
    pygame.image.save(screen, screenshot_path)

# Main loop
running = True
last_move_time = pygame.time.get_ticks()
last_move = None  # Variable to store the last move played

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_time = pygame.time.get_ticks()
    
    # Display the next move every second
    if move_index < len(moves) and current_time - last_move_time >= move_time:
        last_move = board.san(moves[move_index])  # Get the move in SAN format (e.g., e4, e5, Qxe7)
        board.push(moves[move_index])
        draw_board(board, move_index, last_move)
        move_index += 1
        last_move_time = current_time
    elif move_index >= len(moves):  # Stop when all moves are played
        running = False

    clock.tick(30)  # Run at 30 FPS

pygame.quit()
