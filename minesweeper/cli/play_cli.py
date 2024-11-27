from game import Minesweeper, CellState

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

def main():
    width, height, mine_count = 10, 10, 10
    game = Minesweeper(width, height, mine_count)

    while not game.game_over:
        display_board(game)
        command = input("Enter command (r x y / f x y): ").strip().lower()
        try:
            action, x, y = command.split()
            x, y = int(x), int(y)
            if action == 'r':
                game.reveal(x, y)
            elif action == 'f':
                game.flag(x, y)
            else:
                print("Invalid action!")
        except ValueError:
            print("Invalid command!")
            continue

        if game.check_victory():
            print("You win!")
            display_board(game)
            break

    if game.game_over:
        print("Game over!")
        display_board(game)

if __name__ == "__main__":
    main()
