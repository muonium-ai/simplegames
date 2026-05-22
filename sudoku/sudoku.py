from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Hide pygame support prompt
import copy
import json
import os
import random
import sys
import time

import pygame

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
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)

# Fonts
FONT = pygame.font.SysFont("comicsans", 40)
NUMBER_FONT = pygame.font.SysFont("comicsans", 40)
STATUS_FONT = pygame.font.SysFont("comicsans", 24)
TITLE_FONT = pygame.font.SysFont("comicsans", 56)
BUTTON_FONT = pygame.font.SysFont("comicsans", 36)
SMALL_FONT = pygame.font.SysFont("comicsans", 20)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(SCRIPT_DIR, "saved_progress.json")

# Difficulty levels: number of given clues range (min, max)
DIFFICULTIES = {
    "Easy": (36, 40),
    "Medium": (28, 32),
    "Hard": (22, 26),
}
DIFFICULTY_ORDER = ["Easy", "Medium", "Hard"]
DIFFICULTY_RANK = {"Easy": 1, "Medium": 2, "Hard": 3}

# Hand-authored fully-solved Sudoku boards. Picking one and blanking cells
# per difficulty avoids running an expensive generator at startup.
SOLVED_BOARDS = [
    [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ],
    [
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
    ],
    [
        [9, 1, 2, 3, 4, 5, 6, 7, 8],
        [3, 4, 5, 6, 7, 8, 9, 1, 2],
        [6, 7, 8, 9, 1, 2, 3, 4, 5],
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        [4, 5, 6, 7, 8, 9, 1, 2, 3],
        [7, 8, 9, 1, 2, 3, 4, 5, 6],
        [2, 3, 4, 5, 6, 7, 8, 9, 1],
        [5, 6, 7, 8, 9, 1, 2, 3, 4],
        [8, 9, 1, 2, 3, 4, 5, 6, 7],
    ],
    [
        [8, 2, 7, 1, 5, 4, 3, 9, 6],
        [9, 6, 5, 3, 2, 7, 1, 4, 8],
        [3, 4, 1, 6, 8, 9, 7, 5, 2],
        [5, 9, 3, 4, 6, 8, 2, 7, 1],
        [4, 7, 2, 5, 1, 3, 6, 8, 9],
        [6, 1, 8, 9, 7, 2, 4, 3, 5],
        [7, 8, 6, 2, 3, 5, 9, 1, 4],
        [1, 5, 4, 7, 9, 6, 8, 2, 3],
        [2, 3, 9, 8, 4, 1, 5, 6, 7],
    ],
]


def generate_puzzle_for_difficulty(difficulty):
    """Pick a random solved board and blank cells until the desired number of
    clues remains. Returns the puzzle board with zeros at blanked positions."""
    low, high = DIFFICULTIES[difficulty]
    target_clues = random.randint(low, high)
    base = random.choice(SOLVED_BOARDS)
    puzzle = copy.deepcopy(base)
    positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(positions)
    to_blank = 81 - target_clues
    for r, c in positions[:to_blank]:
        puzzle[r][c] = 0
    return puzzle


def load_progress():
    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {"highest_difficulty": "Easy", "puzzles_solved": 0}
        return {
            "highest_difficulty": data.get("highest_difficulty", "Easy"),
            "puzzles_solved": int(data.get("puzzles_solved", 0)),
        }
    except (OSError, ValueError):
        return {"highest_difficulty": "Easy", "puzzles_solved": 0}


def save_progress(progress):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(progress, f)
    except OSError:
        pass


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

def draw_status_bar(win, elapsed_time, message, filled_cells, difficulty):
    status_bar_height = 40
    y = HEIGHT - status_bar_height
    pygame.draw.rect(win, LIGHT_GRAY, (0, y, WIDTH, status_bar_height))
    pygame.draw.line(win, BLACK, (0, y), (WIDTH, y), 2)

    time_text = STATUS_FONT.render(f"Time: {int(elapsed_time)}s", True, BLACK)
    cells_text = STATUS_FONT.render(f"Cells: {filled_cells}/81", True, BLACK)
    diff_text = STATUS_FONT.render(f"Difficulty: {difficulty}", True, BLACK)
    message_text = STATUS_FONT.render(message, True, RED if message else BLACK)

    win.blit(time_text, (8, y + 8))
    win.blit(cells_text, (110, y + 8))
    win.blit(diff_text, (230, y + 8))
    win.blit(message_text, (400, y + 8))

def redraw_window(win, grid, selected_num, elapsed_time, message, difficulty):
    win.fill(WHITE)
    draw_menu(win, selected_num)
    grid.draw(win)
    filled_cells = grid.count_filled()
    draw_status_bar(win, elapsed_time, message, filled_cells, difficulty)
    # Draw "ESC to quit" hint in the top-right corner above the menu bar
    hint_font = pygame.font.SysFont("comicsans", 18)
    hint_text = hint_font.render("ESC to quit", True, BLACK)
    win.blit(hint_text, (WIDTH - hint_text.get_width() - 5, 2))
    pygame.display.update()


def _level_button_rects():
    button_w, button_h = 320, 70
    gap = 24
    start_y = 200
    x = (WIDTH - button_w) // 2
    rects = {}
    for i, name in enumerate(DIFFICULTY_ORDER):
        rects[name] = pygame.Rect(x, start_y + i * (button_h + gap), button_w, button_h)
    return rects


def draw_level_select(win, progress):
    win.fill(WHITE)
    title = TITLE_FONT.render("Sudoku", True, BLACK)
    win.blit(title, ((WIDTH - title.get_width()) // 2, 60))

    subtitle = STATUS_FONT.render("Select difficulty", True, BLACK)
    win.blit(subtitle, ((WIDTH - subtitle.get_width()) // 2, 140))

    rects = _level_button_rects()
    highest = progress.get("highest_difficulty", "Easy")
    for name, rect in rects.items():
        is_highlight = name == highest
        bg = HIGHLIGHT_COLOR if is_highlight else LIGHT_GRAY
        pygame.draw.rect(win, bg, rect)
        pygame.draw.rect(win, BLACK, rect, 3)
        label = BUTTON_FONT.render(name, True, BLUE)
        win.blit(
            label,
            (
                rect.x + (rect.width - label.get_width()) // 2,
                rect.y + (rect.height - label.get_height()) // 2,
            ),
        )

    info = SMALL_FONT.render(
        f"Solved: {progress.get('puzzles_solved', 0)}  |  Highest: {highest}",
        True,
        BLACK,
    )
    win.blit(info, ((WIDTH - info.get_width()) // 2, 470))

    hint = SMALL_FONT.render("ESC to quit", True, BLACK)
    win.blit(hint, (WIDTH - hint.get_width() - 5, 5))

    pygame.display.update()
    return rects


def run_level_select(progress):
    """Block on a level-select screen. Returns the chosen difficulty name."""
    clock = pygame.time.Clock()
    while True:
        rects = draw_level_select(WIN, progress)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for name, rect in rects.items():
                    if rect.collidepoint(pos):
                        return name
        clock.tick(60)


def play_round(difficulty):
    """Play a single round. Returns True if solved, False on quit (handled
    earlier via sys.exit)."""
    puzzle = generate_puzzle_for_difficulty(difficulty)
    grid = Grid(puzzle, WIDTH, WIDTH)
    key = None
    selected_num = None
    start_time = time.time()
    message = ""
    clock = pygame.time.Clock()
    solved_deadline = None  # Non-blocking overlay timer (ticks)

    while True:
        elapsed_time = time.time() - start_time
        # Show "Solved!" overlay until deadline expires
        if solved_deadline is not None:
            redraw_window(WIN, grid, selected_num, elapsed_time, "Solved!", difficulty)
            # Draw centered overlay
            overlay = TITLE_FONT.render("Solved!", True, GREEN)
            WIN.blit(
                overlay,
                (
                    (WIDTH - overlay.get_width()) // 2,
                    (HEIGHT - overlay.get_height()) // 2,
                ),
            )
            pygame.display.update()
            if pygame.time.get_ticks() >= solved_deadline:
                return True
        else:
            redraw_window(WIN, grid, selected_num, elapsed_time, message, difficulty)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                pygame.quit()
                sys.exit(0)

            # Lock out input while solved overlay is showing
            if solved_deadline is not None:
                continue

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
                                message = "Solved!"
                                # Non-blocking deadline pattern (T-000056)
                                solved_deadline = pygame.time.get_ticks() + 1500
                        else:
                            message = "Invalid Move"
                        key = None

        clock.tick(60)


def main():
    progress = load_progress()
    while True:
        difficulty = run_level_select(progress)
        solved = play_round(difficulty)
        if solved:
            progress["puzzles_solved"] = int(progress.get("puzzles_solved", 0)) + 1
            current_rank = DIFFICULTY_RANK.get(progress.get("highest_difficulty", "Easy"), 1)
            new_rank = DIFFICULTY_RANK[difficulty]
            if new_rank > current_rank:
                progress["highest_difficulty"] = difficulty
            save_progress(progress)

    pygame.quit()

if __name__ == "__main__":
    main()
