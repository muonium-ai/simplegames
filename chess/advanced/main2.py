# main2.py

from chess_game.game.chess_game import ChessGame
from chess_game.game.minimax_computer_player import MinimaxComputerPlayer
from chess_game.game.minimax_computer_player2 import MinimaxComputerPlayer2
from chess_game.game.minimax_computer_player3 import MinimaxComputerPlayer3

def main():
    # Initialize the game with enhanced AI players
    game = ChessGame(
        white_player_class=MinimaxComputerPlayer3,  # Strongest AI
        black_player_class=MinimaxComputerPlayer   # Intermediate AI
    )
    game.run()

if __name__ == "__main__":
    main()