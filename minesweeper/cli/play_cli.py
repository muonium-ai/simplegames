import sys
from game import Minesweeper, CellState

def apply_hint(game,winning_message):
    x, y = game.hint()
    game.automark(x, y)
    print(f"Hint: Revealed cell at ({x}, {y})")
    display_board(game)
    # Check for victory after using a hint
    if game.victory:
        print(winning_message)
        sys.exit()

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
    print_status(game)

def print_status(game):
    status = game.get_status()
    print(f"Reveals: {status['reveals']}  Flags: {status['flags']}  Steps: {status['steps']}  Remaining Mines: {status['remaining_mines']}/{status['total_mines']}")

def main(width, height, mine_count):
    game = Minesweeper(width, height, mine_count)
    print("Welcome to Minesweeper!")
    print("Type 'help' to see available commands.")
    winning_message = "Congratulations! You won the game."

    while not game.game_over:
        display_board(game)
        command = input("Enter command (r x y / f x y / h / q / help / quit): ").strip().lower()
        
        if command == 'quit':
            print("Game exited.")
            break
        elif command == 'help':
            print("Commands:")
            print("  r x y - Reveal the cell at (x, y)")
            print("  f x y - Flag the cell at (x, y)")
            print("  h     - Get a hint")
            print("  q     - Quickstart the game (5 hints)")
            print("  quit  - Exit the game")
            print("  help  - Display this help message")
            continue
        elif command == 'h':
            apply_hint(game,winning_message)
            continue
        elif command == 'q':
            game = Minesweeper(width, height, mine_count)
            for _ in range(5):
                apply_hint(game,winning_message)
            continue
        else:
            try:
                parts = command.split()
                if len(parts) != 3:
                    raise ValueError
                action, x_str, y_str = parts
                x, y = int(x_str), int(y_str)

                if action not in ['r', 'f']:
                    print("Invalid action! Use 'r' to reveal or 'f' to flag.")
                    continue

                if not (0 <= x < width and 0 <= y < height):
                    print(f"Invalid coordinates! x and y must be between 0 and {width-1} and 0 and {height-1} respectively.")
                    continue

                if action == 'r':
                    game.reveal(x, y)
                    display_board(game)
                    if game.game_over:
                        if game.victory:
                            print(winning_message)
                        else:
                            print("Mine clicked. Game over.")
                        print("Solution:")
                        game.print_solution()
                        break
                elif action == 'f':
                    game.flag(x, y)
                    display_board(game)

            except ValueError:
                print("Invalid command! Use 'r x y', 'f x y', 'h', 'q', or 'help'.")
                continue

if __name__ == "__main__":
    width = 10
    height = 10
    mine_count = 10
    if len(sys.argv) == 4:
        width, height, mine_count = map(int, sys.argv[1:])
    main(width, height, mine_count)
