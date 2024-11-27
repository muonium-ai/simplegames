from game import Minesweeper, CellState
import sys

def display_board(game):
    for row in game.grid:
        line = []
        for cell in row:
            if cell.state == CellState.HIDDEN:
                line.append('.')
            elif cell.state == CellState.FLAGGED:
                line.append('F')
            elif cell.is_mine:
                line.append('*')
            else:
                line.append(str(cell.neighbor_mines))
        print(' '.join(line))

def main(width, height, mine_count):
    game = Minesweeper(width, height, mine_count)

    while not game.game_over:
        display_board(game)
        command = input("Enter command (r x y / f x y): ").strip().lower()
        try:
            action, x, y = command.split()
            x, y = int(x), int(y)

            # Validate action
            if action not in ['r', 'f']:
                print("Invalid action! Use 'r' to reveal or 'f' to flag.")
                continue

            # Validate coordinates
            if not (0 <= x < width and 0 <= y < height):
                print(f"Invalid coordinates! x and y must be between 0 and {width-1} and 0 and {height-1} respectively.")
                continue

            if action == 'r':
                game.reveal(x, y)
            elif action == 'f':
                game.flag(x, y)

        except ValueError:
            print("Invalid command! Use the format 'r x y' or 'f x y'.")
            continue

        if game.check_victory():
            print("Congratulations! You won the game.")
            break

    if not game.victory:
        print("Mine clicked. Game over.")
        game.print_solution()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        width, height, mine_count = map(int, sys.argv[1:])
    else:
        width, height, mine_count = 10, 10, 10

    main(width, height, mine_count)
