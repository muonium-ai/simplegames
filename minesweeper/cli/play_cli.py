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
    game = Minesweeper(10, 10, 10)

    while not game.game_over:
        display_board(game)
        command = input("Enter command (r x y / f x y): ")
        parts = command.split()
        if len(parts) != 3:
            print("Invalid command!")
            continue
        action, x, y = parts[0], int(parts[1]), int(parts[2])
        if action == 'r':
            game.reveal(x, y)
        elif action == 'f':
            game.flag(x, y)
        else:
            print("Invalid action!")

        if game.check_victory():
            print("You win!")
            break

    if game.game_over:
        print("Game over!")
    display_board(game)

if __name__ == "__main__":
    main()
