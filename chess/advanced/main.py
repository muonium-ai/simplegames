# main.py

from chess_game.game.chess_game import ChessGame
from chess_game.game.chess_player import RandomComputerPlayer

def main():
    # Initialize the game with a human player as White and the computer as Black
    game = ChessGame(
        white_player_class=None,  # None indicates a human player
        black_player_class=RandomComputerPlayer  # Computer plays as Black
    )
    game.run()

if __name__ == "__main__":
    main()