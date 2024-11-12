from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import pygame
import sys
import time

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 640  # Additional height for menu and status bar
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_GRAY = (200, 200, 200)
SELECTED_CELL_COLOR = (189, 214, 255)
HIGHLIGHT_COLOR = (255, 255, 0)
RED = (255, 0, 0)

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)
NUMBER_FONT = pygame.font.SysFont("comicsans", 40)
STATUS_FONT = pygame.font.SysFont("comicsans", 30)

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

class Cell:
    def __init__(self, value, row, col, width, height, editable):
        self.value = value
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.editable = editable
        self.selected = False
        self.highlighted = False

    def draw(self, win):
        gap = self.width / 9
        x = self.col * gap
        y = self.row * gap + 60  # Adjust for menu height

        if self.highlighted:
            pygame.draw.rect(win, HIGHLIGHT_COLOR, (x, y, gap, gap))

        if self.selected:
            pygame.draw.rect(win, SELECTED_CELL_COLOR, (x, y, gap, gap))

        if self.value != 0:
            font_color = GRAY if not self.editable else BLACK
            text = NUMBER_FONT.render(str(self.value), True, font_color)
            win.blit(text, (x + (gap/2 - text.get_width()/2), y + (gap/2 - text.get_height()/2)))

class Grid:
    def __init__(self, board, width, height):
        self.rows = 9
        self.cols = 9
        self.cells = [[Cell(board[i][j], i, j, width, height, board[i][j] == 0) for j in range(9)] for i in range(9)]
        self.width = width
        self.height = height
        self.selected = None

    def draw(self, win):
        # Draw grid lines
        gap = self.width / 9
        for i in range(self.rows+1):
            thickness = 4 if i % 3 == 0 else 1
            pygame.draw.line(win, BLACK, (0, i * gap + 60), (self.width, i * gap + 60), thickness)
            pygame.draw.line(win, BLACK, (i * gap, 60), (i * gap, self.height + 60), thickness)

        # Draw cells
        for row in self.cells:
            for cell in row:
                cell.draw(win)

    def click(self, pos):
        if pos[1] < 60 or pos[1] > self.height + 60:
            return None
        gap = self.width / 9
        x = pos[0] // gap
        y = (pos[1] - 60) // gap
        if x >= 0 and y >= 0 and x < 9 and y <9:
            return (int(y), int(x))
        else:
            return None

    def select(self, row, col):
        for r in self.cells:
            for cell in r:
                cell.selected = False
        self.cells[row][col].selected = True
        self.selected = (row, col)

    def place(self, val):
        row, col = self.selected
        cell = self.cells[row][col]
        if cell.editable:
            if self.valid(val, row, col):
                cell.value = val
                return True
            else:
                return False

    def valid(self, val, row, col):
        # Check row
        for i in range(9):
            if self.cells[row][i].value == val and i != col:
                return False
        # Check column
        for i in range(9):
            if self.cells[i][col].value == val and i != row:
                return False
        # Check square
        start_row = row - row % 3
        start_col = col - col % 3
        for i in range(3):
            for j in range(3):
                cell = self.cells[start_row + i][start_col + j]
                if cell.value == val and (start_row + i, start_col + j) != (row, col):
                    return False
        return True

    def highlight(self, num):
        for row in self.cells:
            for cell in row:
                cell.highlighted = cell.value == num

    def unhighlight(self):
        for row in self.cells:
            for cell in row:
                cell.highlighted = False

    def count_filled(self):
        filled = 0
        for row in self.cells:
            for cell in row:
                if cell.value != 0:
                    filled +=1
        return filled

    def is_solved(self):
        # Check if all cells are filled
        for row in self.cells:
            for cell in row:
                if cell.value == 0:
                    return False
        # Check rows
        for i in range(9):
            nums = []
            for j in range(9):
                val = self.cells[i][j].value
                if val in nums:
                    return False
                nums.append(val)
        # Check columns
        for i in range(9):
            nums = []
            for j in range(9):
                val = self.cells[j][i].value
                if val in nums:
                    return False
                nums.append(val)
        # Check squares
        for box_x in range(3):
            for box_y in range(3):
                nums = []
                for i in range(3):
                    for j in range(3):
                        val = self.cells[box_x*3 + i][box_y*3 + j].value
                        if val in nums:
                            return False
                        nums.append(val)
        return True

def draw_menu(win, selected_num):
    gap = WIDTH / 9
    for i in range(9):
        x = i * gap
        y = 0
        rect = pygame.Rect(x, y, gap, 60)
        if selected_num == i+1:
            pygame.draw.rect(win, LIGHT_GRAY, rect)
        pygame.draw.rect(win, BLACK, rect, 1)
        text = NUMBER_FONT.render(str(i+1), True, RED)
        win.blit(text, (x + (gap/2 - text.get_width()/2), y + (60/2 - text.get_height()/2)))

def draw_status_bar(win, elapsed_time, message, filled_cells):
    status_bar_height = 40
    y = HEIGHT - status_bar_height
    pygame.draw.rect(win, LIGHT_GRAY, (0, y, WIDTH, status_bar_height))
    pygame.draw.line(win, BLACK, (0, y), (WIDTH, y), 2)

    time_text = STATUS_FONT.render(f"Time: {int(elapsed_time)}s", True, BLACK)
    cells_text = STATUS_FONT.render(f"Filled Cells: {filled_cells}/81", True, BLACK)
    message_text = STATUS_FONT.render(message, True, RED if message else BLACK)

    win.blit(time_text, (10, y + 5))
    win.blit(cells_text, (200, y +5))
    win.blit(message_text, (400, y +5))

def redraw_window(win, grid, selected_num, elapsed_time, message):
    win.fill(WHITE)
    draw_menu(win, selected_num)
    grid.draw(win)
    filled_cells = grid.count_filled()
    draw_status_bar(win, elapsed_time, message, filled_cells)
    pygame.display.update()

def main():
    run = True
    grid = Grid(board, WIDTH, WIDTH)
    key = None
    selected_num = None
    start_time = time.time()
    message = ""

    while run:
        elapsed_time = time.time() - start_time
        redraw_window(WIN, grid, selected_num, elapsed_time, message)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] < 60:
                    # Clicked on menu
                    gap = WIDTH / 9
                    x = pos[0] // gap
                    num_clicked = int(x) + 1
                    if selected_num == num_clicked:
                        # Deselect if clicked again
                        selected_num = None
                        grid.unhighlight()
                    else:
                        selected_num = num_clicked
                        grid.unhighlight()
                        grid.highlight(selected_num)
                else:
                    clicked = grid.click(pos)
                    if clicked:
                        row, col = clicked
                        cell = grid.cells[row][col]
                        if cell.editable:
                            grid.select(row, col)
                            key = None
                            message = ""
                    else:
                        grid.selected = None

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

                if grid.selected and key is not None:
                    row, col = grid.selected
                    cell = grid.cells[row][col]
                    if cell.editable:
                        if key == 0:
                            cell.value = 0
                            message = ""
                        elif grid.valid(key, row, col):
                            cell.value = key
                            message = ""
                            # Check if the puzzle is solved
                            if grid.is_solved():
                                message = "Victory!"
                                print("Victory")
                        else:
                            message = "Invalid Move"
                        key = None

    pygame.quit()

if __name__ == "__main__":
    main()
