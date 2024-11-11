# main2.py

from chess_game.game.chess_game import ChessGame
from chess_game.game.chess_player import RandomComputerPlayer

def main():
    # Initialize the game with both players as RandomComputerPlayer
    game = ChessGame(
        white_player_class=RandomComputerPlayer,
        black_player_class=RandomComputerPlayer
    )
    game.run()

if __name__ == "__main__":
    main()