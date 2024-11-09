import pygame
import sys

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simple Sudoku")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
SELECTED_CELL_COLOR = (189, 214, 255)

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)
NUMBER_FONT = pygame.font.SysFont("comicsans", 50)

# Sample Sudoku board (0 represents empty cells)
board = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]

def draw_grid(win):
    gap = WIDTH // 9
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 1
        # Horizontal lines
        pygame.draw.line(win, BLACK, (0, i * gap), (WIDTH, i * gap), thickness)
        # Vertical lines
        pygame.draw.line(win, BLACK, (i * gap, 0), (i * gap, WIDTH), thickness)

def draw_numbers(win, board, selected):
    gap = WIDTH // 9
    for i in range(9):
        for j in range(9):
            x = j * gap
            y = i * gap

            if board[i][j] != 0:
                text = NUMBER_FONT.render(str(board[i][j]), True, BLACK)
                win.blit(text, (x + (gap//2 - text.get_width()//2), y + (gap//2 - text.get_height()//2)))

            if selected == (i, j):
                pygame.draw.rect(win, SELECTED_CELL_COLOR, (x, y, gap, gap))

def redraw_window(win, board, selected):
    win.fill(WHITE)
    draw_grid(win)
    draw_numbers(win, board, selected)
    pygame.display.update()

def main():
    run = True
    selected = None
    key = None

    while run:
        redraw_window(WIN, board, selected)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                gap = WIDTH // 9
                x = pos[0] // gap
                y = pos[1] // gap
                if y < 9:
                    selected = (int(y), int(x))

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    key = 0

                if selected and key is not None:
                    row, col = selected
                    board[row][col] = key
                    key = None

if __name__ == "__main__":
    main()
