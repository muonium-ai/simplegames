# Chess Game

This project implements a simple chess game with different types of players. The players can be either random or use the minimax algorithm to make decisions.

## Project Structure

- `game/player.py`: Contains the abstract class `Player` which defines the interface for chess players. It includes the abstract method `make_move(self, board)` that must be implemented by any subclass.
  
- `game/random_computer_player.py`: Implements the `RandomComputerPlayer` class that inherits from `Player`. This class selects a random legal move from the given chess board.

- `game/minimax_computer_player.py`: Implements the `MinimaxComputerPlayer` class that also inherits from `Player`. This class uses the minimax strategy to determine the best move based on a specified depth.

## Usage

To use the players, import them from their respective modules and create instances as needed. You can then call the `make_move` method to get the player's move based on the current state of the chess board.

## Requirements

- Python 3.x
- chess library (install via pip)

## License

This project is licensed under the MIT License.