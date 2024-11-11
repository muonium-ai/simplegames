# main2.py

from chess_game.game.chess_game import ChessGame
from chess_game.game.chess_player import RandomComputerPlayer, MinimaxComputerPlayer

def main():
    # Initialize the game with both players as RandomComputerPlayer
    game = ChessGame(
        white_player_class=MinimaxComputerPlayer,
        black_player_class=RandomComputerPlayer
    )
    game.run()

if __name__ == "__main__":
    main()