# config.py

# Screen configuration
SCREEN_WIDTH = 520
SCREEN_HEIGHT = 560
SQUARE_SIZE = 60
LABEL_OFFSET = 20

# Colors
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68)
LABEL_COLOR = (0, 0, 0)
WHITE_PIECE_COLOR = (255, 255, 255)
BLACK_PIECE_COLOR = (0, 0, 0)

# Unicode pieces
UNICODE_PIECES = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

# Board labels (from Black's perspective)
COLUMNS = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
ROWS = ['1', '2', '3', '4', '5', '6', '7', '8']