from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
import chess
import chess.pgn
import sys
import os

# Initialize Pygame
pygame.init()
screen_size = 800  # Screen size for the chessboard display
square_size = screen_size // 8
info_height = 100  # Space above the board for displaying game details
screen = pygame.display.set_mode((screen_size, screen_size + info_height))
pygame.display.set_caption("Chess Replay")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
light_square = (222, 184, 135)  # A darker shade of beige for better contrast
dark_square = (181, 136, 99)
info_bg_color = (200, 220, 240)  # Light blue background for info screen

# Unicode chess pieces
unicode_pieces = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # White pieces
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'   # Black pieces
}

# Load PGN file and extract games
pgn_file = sys.argv[1] if len(sys.argv) > 1 else "games.pgn"
game_name = os.path.splitext(os.path.basename(pgn_file))[0]
screenshot_dir = os.path.join("screenshots", game_name)
os.makedirs(screenshot_dir, exist_ok=True)

# Extract all games from the PGN file
with open(pgn_file) as f:
    games = []
    while True:
        game = chess.pgn.read_game(f)
        if game is None:
            break
        games.append(game)

# Fonts
pygame.font.init()
font = pygame.font.SysFont("Segoe UI Symbol", square_size - 10)
info_font = pygame.font.SysFont("Arial", 24)

def show_game_details(game, game_id, game_dir):
    screen.fill(info_bg_color)  # Set background color for info screen
    event = game.headers.get("Event", "Unknown Event")
    white_player = game.headers.get("White", "Unknown White")
    black_player = game.headers.get("Black", "Unknown Black")
    date = game.headers.get("Date", "Unknown Date")
    result = game.headers.get("Result", "Unknown Result")
    
    # Display game details, including result
    lines = [
        f"Game ID: {game_id}",
        f"Event: {event}",
        f"White: {white_player}",
        f"Black: {black_player}",
        f"Date: {date}",
        f"Result: {result}"
    ]
    for i, line in enumerate(lines):
        text_surface = info_font.render(line, True, black)
        screen.blit(text_surface, (20, 30 + i * 30))
    
    pygame.display.flip()
    pygame.time.delay(2000)  # Display game details for 2 seconds

    # Save screenshot of the game info (including result)
    info_screenshot_path = os.path.join(game_dir, "info.png")
    pygame.image.save(screen, info_screenshot_path)

def draw_board(board, move_index, last_move):
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
            color = light_square if (row + col) % 2 == 0 else dark_square
            pygame.draw.rect(screen, color, pygame.Rect(col * square_size, row * square_size + info_height, square_size, square_size))
            
            # Draw pieces
            piece = board.piece_at(chess.square(col, 7 - row))
            if piece:
                piece_unicode = unicode_pieces[piece.symbol()]
                text_surface = font.render(piece_unicode, True, black if piece.color == chess.WHITE else white)
                text_rect = text_surface.get_rect(center=(col * square_size + square_size // 2, row * square_size + info_height + square_size // 2))
                screen.blit(text_surface, text_rect)

    pygame.display.flip()

def play_game(game, game_id):
    # Initialize board and moves
    board = game.board()
    moves = list(game.mainline_moves())
    move_index = 0
    last_move = None

    # Create subfolder for each game
    game_dir = os.path.join(screenshot_dir, game_id)
    os.makedirs(game_dir, exist_ok=True)

    # Show game details and capture info screenshot
    show_game_details(game, game_id, game_dir)

    # Initialize clock within play_game function
    clock = pygame.time.Clock()

    running = True
    last_move_time = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        current_time = pygame.time.get_ticks()
        
        # Display the next move every 0.1 seconds
        if move_index < len(moves) and current_time - last_move_time >= 100:
            last_move = board.san(moves[move_index])
            board.push(moves[move_index])
            draw_board(board, move_index, last_move)
            move_index += 1
            last_move_time = current_time
            
            # Save screenshot for each move
            screenshot_path = os.path.join(game_dir, f"{move_index:03}.png")
            pygame.image.save(screen, screenshot_path)
        
        elif move_index >= len(moves):  # Exit when all moves are played
            pygame.time.delay(2000)  # Pause for 2 seconds at end of game
            running = False

        clock.tick(30)

# Main loop to process all games
for i, game in enumerate(games):
    game_id = f"game_{i+1}"
    play_game(game, game_id)

pygame.quit()
