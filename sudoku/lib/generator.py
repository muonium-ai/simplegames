# lib/generator.py

import random
import copy

def generate_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_board(board)
    return board

def fill_board(board):
    numbers = list(range(1, 10))
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                random.shuffle(numbers)
                for num in numbers:
                    if valid(board, num, (i, j)):
                        board[i][j] = num
                        if check_board_full(board):
                            return True
                        else:
                            if fill_board(board):
                                return True
                break
        else:
            continue
        break
    board[i][j] = 0
    return False

def check_board_full(board):
    for row in board:
        if 0 in row:
            return False
    return True

def valid(board, num, pos):
    # Check row
    for i in range(9):
        if board[pos[0]][i] == num and pos[1] != i:
            return False
    # Check column
    for i in range(9):
        if board[i][pos[1]] == num and pos[0] != i:
            return False
    # Check square
    start_row = pos[0] - pos[0]%3
    start_col = pos[1] - pos[1]%3
    for i in range(3):
        for j in range(3):
            if board[start_row+i][start_col+j] == num and (start_row+i, start_col+j) != pos:
                return False
    return True

def remove_numbers(board, attempts=5):
    # Remove numbers to create a puzzle
    puzzle = copy.deepcopy(board)
    while attempts > 0:
        row = random.randint(0,8)
        col = random.randint(0,8)
        while puzzle[row][col] == 0:
            row = random.randint(0,8)
            col = random.randint(0,8)
        backup = puzzle[row][col]
        puzzle[row][col] = 0

        # Make a copy and try to solve it
        board_copy = copy.deepcopy(puzzle)
        solutions = [0]
        solve(board_copy, solutions)
        if solutions[0] != 1:
            # Not unique solution, restore the cell
            puzzle[row][col] = backup
            attempts -=1
    return puzzle

def solve(board, solutions, limit=2):
    find = find_empty(board)
    if not find:
        solutions[0] += 1
        return True
    else:
        row, col = find
    for num in range(1,10):
        if valid(board, num, (row, col)):
            board[row][col] = num
            if solve(board, solutions, limit):
                if solutions[0] >= limit:
                    return True
            board[row][col] = 0
    return False

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def generate_puzzle(difficulty=5):
    board = generate_board()
    puzzle = remove_numbers(board, attempts=difficulty)
    return puzzle
